from flask import Flask, jsonify, request
import logging, psycopg2, time, jwt, datetime

app = Flask(__name__)
KEY = "b96ZhIxcBdxNPDn4WRzDueMMqyux3k7g"


@app.route('/')
def hello():
    return """

    Bem vindo à segunda meta do projeto de Base de dados!  <br/>
    <br/>
    Trabalho realizado por:<br/>
    <br/>
    Diogo Filipe    | uc2018288391@student.uc.pt<br/>
    José Gomes      | uc2018286225@student.uc.pt<br/>
    Pedro Marques   | uc2018285632@student.uc.pt<br/>
    <br/>
    """


##
##      Registo de Utilizadores
##
## -Criar um novo utilizador, inserindo os dados requeridos pelo modelo de dados.
##
## [Argumentos a inserir...]
##
##

@app.route("/dbproj/user", methods=['POST'])
def addUser():
    logger.info("###              BD [Insert User]: POST /dbproj/user              ###");
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new user  ----")
    logger.debug(f'payload: {payload}')

    # Validacoes

    # parameterized queries, good for security and performance
    statement = """
                  INSERT INTO utilizador (username, email, password) 
                          VALUES ( %s,   %s ,   %s ) RETURNING userid"""

    try:
        values = (payload["username"], payload["email"], payload["password"])
    except (Exception) as error:
        codigoErro = '003'  # Payload incorreto (nome das variaveis)
        return jsonify(erro=codigoErro)

    if not ((32 >= len(values[0]) > 0) and (64 >= len(values[1]) > 0) and (32 >= len(values[2]) > 0)):
        codigoErro = '002'  # Input Invalido
        return jsonify(erro=codigoErro)

    try:
        cur.execute(statement, values)
        sucess = True
        novoUserId = str(cur.fetchone()[0])
        cur.execute("commit")
    except psycopg2.IntegrityError:
        sucess = False
        codigoErro = '001'  # Utilizador duplicado
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        sucess = False
        codigoErro = '999'  # Erro nao identificado
    finally:
        if conn is not None:
            conn.close()
    if (sucess):
        return jsonify(userId=novoUserId)
    else:
        return jsonify(erro=codigoErro)


@app.route("/dbproj/user", methods=['PUT'])
def loginUser():
    logger.info("###              BD [Login User]: PUT /dbproj/user              ###");
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- login  ----")
    logger.debug(f'payload: {payload}')

    # Validacoes
    try:
        values = (payload["username"], payload["password"])
    except Exception as error:
        codigoErro = '003'  # Payload incorreto
        return jsonify(erro=codigoErro)

    username = payload["username"]
    password = payload["password"]
    if len(username) < 1 or len(username) > 32 or len(password) < 1 or len(password) > 32:
        codigoErro = '002'  # Payload incorreto
        return jsonify(erro=codigoErro)

    cur.execute("SELECT userid FROM utilizador WHERE username = %s and password = %s", (username, password))
    rows = cur.fetchall()

    if len(rows) == 0:
        codigoErro = '004'  # Credenciais incorretas
        return jsonify(erro=codigoErro)

    userid = rows[0][0]

    time_limit = datetime.datetime.utcnow() + datetime.timedelta(minutes=30)  # set limit for user
    payload = {"userid": rows[0][0], "exp": time_limit}
    token = jwt.encode(payload, KEY)

    statement = """
                    UPDATE utilizador 
                      SET authtoken = %s
                    WHERE userid = %s"""

    values = (token, userid)

    try:
        cur.execute(statement, values)
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999'
        return jsonify(erro=codigoErro)
    finally:
        if conn is not None:
            conn.close()

    return jsonify(authToken=token)


@app.route("/dbproj/leiloes", methods=['GET'], strict_slashes=True)
def get_all_auctions():
    logger.info("###              BD [LIST AUCTIONS]: GET /dbproj/leiloes              ###")

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT leilaoid, descricao FROM leilao WHERE datafim > (NOW() + INTERVAL '1 hours')")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify(erro='999')

    rows = cur.fetchall()

    payload = []
    logger.debug("---- Leiloes  ----")
    for row in rows:
        logger.debug(row)
        content = {'leilaoId': int(row[0]), 'descricao': row[1]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)


@app.route("/dbproj/leiloes/<keyword>", methods=['GET'])
def get_auction(keyword):
    logger.info("###              BD [Get auction(s)]: GET /dbproj/leiloes/<keyword>              ###");

    logger.debug(f'keyword: {keyword}')

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT leilaoid, descricao FROM leilao WHERE datafim > (NOW() + INTERVAL '1 hours') and artigoid = %s", (keyword,) )
    rows = cur.fetchall()
    payload = []

    if len(rows) == 1:
        row = rows[0]
        logger.debug("---- selected auction  ----")
        logger.debug(row)
        content = {'leilaoId': int(row[0]), 'descricao': row[1]}
        payload.append(content)  # appending to the payload to be returned
        conn.close()
        return jsonify(payload)

    query = '%' + keyword + '%'
    cur.execute("SELECT leilaoid, descricao FROM leilao WHERE datafim > (NOW() + INTERVAL '1 hours') and LOWER(descricao) LIKE %s",
                (query,))
    rows = cur.fetchall()

    if len(rows) == 0:
        conn.close()
        return jsonify(payload)

    logger.debug("---- selected auction(s)  ----")
    for row in rows:
        logger.debug(row)
        content = {'leilaoId': int(row[0]), 'descricao': row[1]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)


def checkIdUtilizador(idVendedor):
    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT utilizador_userid FROM vendedor WHERE utilizador_userid = %s ", (idVendedor,))
    rows = cur.fetchall()

    if len(rows) == 0:
        codigoErro = '004'  # Credenciais incorretas
        return False
    return True


@app.route("/dbproj/leilao", methods=['POST'])
def criaLeilao():
    logger.info("###              BD [Insert Auction]: POST /dbproj/leilao              ###");
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- New Action  ----")
    logger.debug(f'payload: {payload}')

    # parameterized queries, good for security and performance
    statement = """
                  INSERT INTO leilao (precominimo, titulo, descricao, datafim, artigoid, nomeartigo, vendedor_utilizador_userid) 
                          VALUES ( %s,   %s ,   %s ,  %s , %s , %s , %s) RETURNING leilaoid """

    # VERIFICACOES
    try:
        values = (
            payload["leilaoPrecoMinimo"], payload["leilaoTitulo"], payload["leilaoDescricao"], payload["leilaoDataFim"],
            payload["artigoId"], payload["nomeArtigo"], payload["vendedorID"])
    except Exception as error:
        codigoErro = '003'
        return jsonify(erro=codigoErro)

    try:
        precoMin = int(payload["leilaoPrecoMinimo"])
        idVendedor = int(payload["vendedorID"])
    except (Exception, ValueError) as error:
        codigoErro = '003'
        return jsonify(erro=codigoErro)

    if not ((64 >= len(values[1]) > 0) and (512 >= len(values[2]) > 0) and (10 >= len(values[4]) > 0) and (
            64 >= len(values[5]) > 0)):
        if (checkIdUtilizador(values[6]) != True):
            codigoErro = '009'  # ID Vendedor inexistente
        else:
            codigoErro = '002'  # Input Invalido
        return jsonify(erro=codigoErro)

    try:
        cur.execute(statement, values)
        sucess = True
        leilaoID = str(cur.fetchone()[0])
        cur.execute("commit")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        sucess = False
        codigoErro = '999'  # Erro nao identificado
    finally:
        if conn is not None:
            conn.close()

    if sucess:
        return jsonify(leilaoId=leilaoID)
    else:
        return jsonify(leilaoId=codigoErro)


@app.route("/dbproj/leilao/<leilao_leilaoid>", methods=['GET'], strict_slashes=True)
def getDetailsAuction(leilao_leilaoid):
    codigoErro = ''
    payload = []
    sucess = False
    logger.info("###              BD [Get Auction]: Get /dbproj/leilao/<leilao_leilaoid>              ###");

    conn = db_connection()
    cur = conn.cursor()


    sql = "SELECT leilaoid, titulo, descricao, datafim, artigoid, nomeartigo, maiorlicitacao, username " \
          "FROM leilao, utilizador, vendedor WHERE leilaoid = %s AND vendedor_utilizador_userid = userid "

    try:
        leilaoID = int(leilao_leilaoid)
    except (Exception, ValueError) as error:
        codigoErro = '003'
        return jsonify(erro=codigoErro)

    try:
        cur.execute(sql, f'{leilao_leilaoid}')
        rows = cur.fetchall()

        logger.debug("---- Auction Details  ----")

        if len(rows) == 0:
            codigoErro = '007'
            return jsonify(erro=codigoErro)

        payload.append({"DETALHES DO LEILAO": leilao_leilaoid})
        for row in rows:
            logger.debug(row)
            content = {'leilaoid': int(row[0]), 'titulo': row[1], 'descricao': row[2], 'datafim': row[3],
                       'artigoid': row[4], 'nomeartigo': row[5],  'maiorlicitcao': row[6],
                       'username': row[7]}
            payload.append(content)  # appending to the payload to be returned

        sql = "SELECT id, comentario, momento, username " \
              "FROM mensagem, utilizador WHERE leilao_leilaoid = %s AND utilizador_userid = userid "


        try:
            cur.execute(sql, f'{leilao_leilaoid}')
            rows = cur.fetchall()

            if len(rows) == 0:
                codigoErro = 'Nao ha mensagens'
                

            logger.debug("---- Mural Details  ----")
            payload.append({"DETALHES DO MURAL LEILAO": leilao_leilaoid})
            for row in rows:
                logger.debug(row)
                content = {'id': int(row[0]), 'comentario': row[1], 'momento': row[2], 'username': row[3]}
                payload.append(content)  # appending to the payload to be returned

            sql = "SELECT id, valor, username " \
                  "FROM licitacao, utilizador WHERE leilao_leilaoid = %s AND comprador_utilizador_userid = userid "
            cur.execute(sql, f'{leilao_leilaoid}')
            rows = cur.fetchall()

            if len(rows) == 0: #Nao ha licitacoes
                codigoErro = 'Nao ha licitacoes'


            logger.debug("---- Bids Details  ----")
            payload.append({"DETALHES DAS LICITACOES LEILAO": leilao_leilaoid})
            sucess = True
            for row in rows:
                logger.debug(row)
                content = {'id': int(row[0]), 'valor': row[1], 'username': row[2]}
                payload.append(content)  # appending to the payload to be returned

        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            codigoErro = '999'
            return jsonify(erro=codigoErro)

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        sucess = False
        codigoErro = '999'  # Erro nao identificado
    finally:
        if conn is not None:
            conn.close()

        if sucess:
            return jsonify(payload)
        else:
            return jsonify(erro=codigoErro)

@app.route("/dbproj/leilao/<leilao_leilaoid>", methods=['PUT'])
def alteraPropriedadeLeilao(leilao_leilaoid):
    codigoErro = ''
    payload = []
    sucess = False
    logger.info(
        "###              BD [Change Auction Properties]: Get /dbproj/leilao/<leilao_leilaoid>              ###");

    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()

    sql = "SELECT leilaoid, titulo, descricao " \
          "FROM leilao WHERE leilaoid = %s "

    try:
        leilaoID = int(leilao_leilaoid)
    except (Exception, ValueError) as error:
        codigoErro = '003'  # NAO É NUMERO
        return jsonify(erro=codigoErro)

    try:
        cur.execute(sql, f'{leilao_leilaoid}')

        rows = cur.fetchall()

        if len(rows) == 0:
            codigoErro = '002'  # Input invalido
            return jsonify(erro=codigoErro)

        newTitle = payload['novoTitulo']
        newDescription = payload['novaDescricao']
        for row in rows:
            leilaoID = int(row[0])
            currentTitle = row[1]
            currentDescription = row[2]

        # COLOCAR LEILAO ORIGINAL NA TABELA DE VERSAO
        sql = "INSERT INTO versao (titulo, descricao, leilao_leilaoid)" \
              "VALUES (%s,  %s,  %s)"
        try:
            values = (currentTitle, currentDescription, leilaoID)
        except (Exception) as error:
            codigoErro = '003'  # Payload incorreto (nome das variaveis)
            return jsonify(erro=codigoErro)

        try:
            cur.execute(sql, values)
            cur.execute("commit")
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            sucess = False
            codigoErro = '999'  # Erro nao identificado

        if not ((64 >= len(newTitle) > 1) and 512 >= len(newDescription) > 1):
            codigoErro = '002'  # Input Invalido
            return jsonify(erro=codigoErro)

        if len(newTitle) == 0:
            newTitle = currentTitle

        if len(newDescription) == 0:
            newDescription = currentDescription

        if len(newTitle) == 0 and len(newDescription) == 0 or currentTitle == newTitle and currentDescription == newDescription:
            codigoErro = '002'  # As alteracoes estao vazias/iguais e nao se altera nada
            return jsonify(erro=codigoErro)

        sql = "UPDATE leilao " \
              "SET titulo = %s,  descricao = %s " \
              "WHERE leilaoid = %s "

        values = (newTitle, newDescription, leilao_leilaoid)
        try:
            cur.execute(sql, values)
            cur.execute("commit")
            sucess = True
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(error)
            codigoErro = '999'
            return jsonify(erro=codigoErro)

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        sucess = False
        codigoErro = '999'  # Erro nao identificado
    finally:
        if conn is not None:
            conn.close()

        if sucess:
            return jsonify(payload)
        else:
            return jsonify(erro=codigoErro)


@app.route("/dbproj/leilao/ban/", methods=['PUT'], strict_slashes=True)
def banUser():
    codigoErro = ''
    payload = []
    sucess = False
    logger.info("###              BD [Ban User Auction]: Put /dbproj/leilao/ban/<userid>             ###");

    payload = request.get_json()
    conn = db_connection()
    cur = conn.cursor()

    # TODO
    # JSON RECEBE o admin e o user a banir - DONE
    # Colocar ID Admin na tabela utilizador na linha do user a banir - DONE
    # Verificar se o user tem algum leilao a decorrer - DONE
    # Caso tenha, invalidar a licitacao se tiver, alterar o parametro valida - DONE
    # Obter a maior licitacao  e corresponder o seu valor ao valor da invalida - DONE
    # Colocar no mural dos leiloes uma msg de incomodo e paa cada utilizador enviar uma notifcacao

    # Colocar ID Admin na tabela utilizador na linha do user a banir
    sql = "UPDATE utilizador " \
          "SET adminbaniu = %s " \
          "WHERE userid = %s"

    try:
        values = (payload['adminID'], payload['userID'])
    except (Exception, ValueError) as error:
        codigoErro = '003'
        return jsonify(erro=codigoErro)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999'
        return jsonify(erro=codigoErro)

    try:
        cur.execute(sql, values)
        cur.execute("commit")
        #sucess = True
        #logger.debug("---- Auction Details  ----")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999'
        return jsonify(erro=codigoErro)

    # Verificar se o user tem algum leilao a decorrer
    sql = "SELECT * " \
          "FROM leilao " \
          "WHERE vendedor_utilizador_userid = %s AND datafim > (NOW() + INTERVAL '1 hours')"

    try:
        values = [payload['userID']]
        cur.execute(sql, values)
        rows = cur.fetchall()

        if len(rows) == 0: # Significa que nao esta a vender nada atualmente
            codigoErro = '008' # User nao tem leiloes a decorrer

        else: # Significa que tem leiloes ativos e temos de as cancelar
            sql = "UPDATE leilao " \
                  "SET admincancelou = %s " \
                  "WHERE vendedor_utilizador_userid = %s"

            values = (payload['adminID'], payload['userID'])
            try:
                cur.execute(sql, values)
                cur.execute("commit")
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(error)
                codigoErro = '999'
                return jsonify(erro=codigoErro)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999'
        logger.debug('SAIII:')
        return jsonify(erro=codigoErro)

    # Verificar se o user a banir tem alguma licitacao e invalida-la
    sql = "UPDATE licitacao " \
          "SET valida = false " \
          "WHERE comprador_utilizador_userid = %s"

    values = [payload['userID']]
    affected_rows = 0
    try:
        cur.execute(sql, values)
        affected_rows = cur.rowcount
        cur.execute("commit")
        logger.debug(f'ROWS AFFECTED: {affected_rows}')
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999' # comprador invalido ou nao tem licitacoes

        return jsonify(erro=codigoErro)

    if affected_rows == 0: #Significa que o user nao tinha licitacoes
        codigoErro = '019'
        return jsonify(erro=codigoErro)
    else: #Significa que o user tinha licitacoes
        # E preciso obter o valor da licitacao max do user de todos os leiloes
        sql = "SELECT leilao_leilaoid FROM licitacao WHERE comprador_utilizador_userid = %s "
        values = [payload['userID']]
        cur.execute(sql ,values)
        rows = cur.fetchall()

        for row in rows: #Vou percorrer cada leilao que ele pertence para modificar as licitacoes
            leilaoID = row[0]
            logger.debug(f'LEILAO ID: {leilaoID}, TYPE: {type(leilaoID)}')

            sqlQuery = "SELECT MAX(valor) FROM licitacao WHERE comprador_utilizador_userid = %s and leilao_leilaoid = %s "
            sqlValues = (payload['userID'], leilaoID)
            cur.execute(sqlQuery, sqlValues)
            maxValueUser = cur.fetchall()[0]

            sqlQuery = "SELECT MAX(valor) FROM licitacao WHERE leilao_leilaoid = %s "
            cur.execute(sqlQuery, [leilaoID])
            maxBidAuction = cur.fetchall()[0]

            if  maxValueUser < maxBidAuction: #invalidar todas as licitacoes entre estes 2 valores e colocar a maior licitacao com o valor do user a banir
                sqlQuery = "UPDATE licitacao SET valida = "\
                                        "CASE " \
                                            "WHEN valor = %s THEN true " \
                                            "WHEN valor >= %s AND valor < %s THEN false " \
                                            "ELSE true "\
                                        "END, " \
                                    "valor = "\
                                        "CASE " \
                                            "WHEN valor = %s THEN %s "\
                                            "ELSE valor " \
                                        "END "\
                            "WHERE leilao_leilaoid = %s"

                values = (maxBidAuction, maxValueUser, maxBidAuction, maxBidAuction, maxValueUser, leilaoID)
                try:
                    cur.execute(sqlQuery, values)
                    cur.execute("commit")
                except (Exception, psycopg2.DatabaseError) as error:
                    logger.error(error)
                    codigoErro = '999'
                    return jsonify(erro=codigoErro)

            # Colocar no mural dos leiloes uma msg de incomodo e paa cada utilizador enviar uma notificacao
            sqlQuery = "INSERT INTO mensagem (comentario, momento, utilizador_userid, leilao_leilaoid)" \
                        "VALUES (%s, NOW(), %s , %s)"

            try:
                comentario = f"Lamentamos o incomodo mas o utilizador {payload['userID']} foi banido do leilao {leilaoID}"
                values = (comentario, payload['userID'], leilaoID)
            except (Exception, ValueError) as error:
                codigoErro = '003'
                return jsonify(erro=codigoErro)

            try:
                cur.execute(sqlQuery, values)
                cur.execute("commit")
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(error)
                sucess = False
                codigoErro = '999'  # Erro nao identificado

            comentario = f"Utilizador {payload['userID']} foi banido do leilao {leilaoID}"
            sqlQuery = "INSERT INTO notificacao (comentario, momento, utilizador_userid) "\
                        "SELECT %s, NOW(), comprador_utilizador_userid " \
                       "FROM licitacao WHERE leilao_leilaoid = %s"

            values = (comentario, leilaoID)
            try:
                cur.execute(sqlQuery, values)
                cur.execute("commit")
            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(error)
                sucess = False
                codigoErro = '999'  # Erro nao identificado
            # else: NAO E PRECISO FAZER NADA PQ A LICITACAO DO USER E MAIXIMA ENTAO CONTA A SEGUNDA MELHOR


    try:
        sucess = True
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        sucess = False
        codigoErro = '999'  # Erro nao identificado

    finally:
        if conn is not None:
            conn.close()

        if sucess:
            return jsonify(payload)
        else:
            return jsonify(erro=codigoErro)



@app.route("/dbproj/leiloesAtividade", methods=['GET'], strict_slashes=True)
def listAuctionsByUser():
    logger.info("###              BD [Get Auction By User]: Get /dbproj/leiloesAtividade              ###");

    headers = request.headers
    conn = db_connection()
    cur = conn.cursor()

    try:
        authCode = headers['authToken']
    except (Exception) as error:
        codigoErro = '003'  # Payload incorreto (nome das variaveis)
        return jsonify(erro=codigoErro)

    userId = getUserIdByAuthCode(authCode)
    if(userId[0] == None):
        return jsonify(erro=userId[1])
    userId = userId[0]
    #return jsonify(Encontrei=userId) #DEBUG

    statement = "SELECT leilaoid, titulo, descricao, datafim, artigoid, nomeartigo, maiorlicitacao" \
                " FROM leilao AS l" \
                " WHERE ((SELECT COUNT(*) FROM leilao AS l2 WHERE vendedor_utilizador_userid = %s AND l2.leilaoid = l.leilaoid) +" \
    	" (SELECT COUNT(*) FROM licitacao AS l3 WHERE comprador_utilizador_userid = %s AND l3.leilao_leilaoid = l.leilaoid)) > 0"

    cur.execute(statement, (userId, userId,))
    rows = cur.fetchall()
    payload = []
    for row in rows:
        content = {'leilaoid': int(row[0]), 'titulo': row[1], 'descricao': row[2], 'datafim': row[3],
                       'artigoid': row[4], 'nomeartigo': row[5], 'maiorlicitcao': row[6]}
        payload.append(content)  # appending to the payload to be returned

    return jsonify(payload)

def getUserIdByAuthCode(authCode):
    userId = None

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT userid FROM utilizador WHERE authToken = %s", (authCode,))
        rows = cur.fetchall()
        if(len(rows) != 1):
            codigoErro = '005'  # Utilizador nao registado na base de dados
            return (None, codigoErro)
        userId = rows[0]
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999'  # Erro nao identificado
        return (None, codigoErro)
    finally:
        if conn is not None:
            conn.close()

    return userId
			
def db_connection():
    db = psycopg2.connect(user="aulaspl",
                          password="aulaspl",
                          host="db",
                          port="5432",
                          database="bdLeiloes")
    return db


if __name__ == "__main__":
    # Set up the logging
    logging.basicConfig(filename="logs/log_file.log")
    logger = logging.getLogger('logger')
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]:  %(message)s',
                                  '%H:%M:%S')
    # "%Y-%m-%d %H:%M:%S") # not using DATE to simplify
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    time.sleep(1)  # just to let the DB start before this print :-)

    logger.info("\n---------------------------------------------------------------\n" +
                "API v1.0 online: http://localhost:8080/\n\n")

    app.run(host="0.0.0.0", debug=True, threaded=True)
