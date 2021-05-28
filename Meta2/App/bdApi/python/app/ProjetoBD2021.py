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


@app.route("/dbproj/vendedor", methods=['POST'])
def addVendedor():
    logger.info("###              BD [Insert Seller]: POST /dbproj/vendedor              ###")
    payload = request.get_json()
    headers = request.headers
    logger.info("---- new vendedor  ----")
    logger.debug(f'payload: {payload}')

    try:
        authCode = headers['authToken']
        moradaEnvio = payload['moradaEnvio']
        if(len(moradaEnvio)>128):
            codigoErro = '002'  # Payload incorreto (nome das variaveis)
            return jsonify(erro=codigoErro)
    except (Exception) as error:
        codigoErro = '003'  # Payload incorreto (nome das variaveis)
        return jsonify(erro=codigoErro)

    userId = getUserIdByAuthCode(authCode)
    if (userId[0] == None):
        return jsonify(erro=userId[1])
    userId = userId[0]

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO vendedor (moradaenvio, utilizador_userid) VALUES (%s , %s) RETURNING utilizador_userid", (moradaEnvio, userId,))
        sucess = True
        novoVendedorId = str(cur.fetchone()[0])
        cur.execute("commit")
    except psycopg2.IntegrityError:
        sucess = False
        codigoErro = '016'  # Vendedor Duplicado
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        sucess = False
        codigoErro = '999'  # Erro nao identificado
    finally:
        if conn is not None:
            conn.close()
    if (sucess):
        return jsonify(vendedorId=novoVendedorId)
    else:
        return jsonify(erro=codigoErro)

@app.route("/dbproj/comprador", methods=['POST'])
def addComprador():
    logger.info("###              BD [Insert Buyer]: POST /dbproj/comprador              ###")
    payload = request.get_json()
    headers = request.headers
    logger.info("---- new comprador  ----")
    logger.debug(f'payload: {payload}')

    try:
        authCode = headers['authToken']
        moradaRececao = payload['moradaRececao']
        if(len(moradaRececao)>128):
            codigoErro = '002'  # Payload incorreto (nome das variaveis)
            return jsonify(erro=codigoErro)
    except (Exception) as error:
        codigoErro = '003'  # Payload incorreto (nome das variaveis)
        return jsonify(erro=codigoErro)

    userId = getUserIdByAuthCode(authCode)
    if (userId[0] == None):
        return jsonify(erro=userId[1])
    userId = userId[0]

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO comprador (moradarececao, utilizador_userid) VALUES (%s , %s) RETURNING utilizador_userid", (moradaRececao, userId,))
        sucess = True
        novoCompradorId = str(cur.fetchone()[0])
        cur.execute("commit")
    except psycopg2.IntegrityError:
        sucess = False
        codigoErro = '017'  # Comprador Duplicado
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        sucess = False
        codigoErro = '999'  # Erro nao identificado
    finally:
        if conn is not None:
            conn.close()
    if (sucess):
        return jsonify(compradorId=novoCompradorId)
    else:
        return jsonify(erro=codigoErro)

@app.route("/dbproj/admin", methods=['POST'])
def addAdmin():
    logger.info("###              BD [Insert Admin]: POST /dbproj/admin              ###")
    headers = request.headers
    logger.info("---- new admin  ----")

    try:
        authCode = headers['authToken']
    except (Exception) as error:
        codigoErro = '002'  # Payload/Header incorreto (nome/tamanho das variáveis)
        return jsonify(erro=codigoErro)

    userId = getUserIdByAuthCode(authCode)
    if (userId[0] == None):
        return jsonify(erro=userId[1])
    userId = userId[0]

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO administrador (utilizador_userid) VALUES (%s) RETURNING utilizador_userid", (userId,))
        sucess = True
        novoAdminId = str(cur.fetchone()[0])
        cur.execute("commit")
    except psycopg2.IntegrityError:
        sucess = False
        codigoErro = '018'  # Administrador Duplicado
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        sucess = False
        codigoErro = '999'  # Erro nao identificado
    finally:
        if conn is not None:
            conn.close()
    if (sucess):
        return jsonify(adminId=novoAdminId)
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
    headers = request.headers
    authCode = headers["authToken"]

    vendedorID = getVendedorIdByAuthCode(authCode)
    if (vendedorID[0] == None):
        return jsonify(erro=vendedorID[1])
    vendedorID = vendedorID[0]

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
            payload["artigoId"], payload["nomeArtigo"], vendedorID)
    except Exception as error:
        codigoErro = '003'
        return jsonify(erro=codigoErro)

    try:
        precoMin = int(payload["leilaoPrecoMinimo"])
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


def higherBidNotification(compradorId, licitacao, leilaoId):
    codigoErro = ''
    sucess = False
    payload = []
    conn = db_connection()
    cur = conn.cursor()

    sql = "SELECT comprador_utilizador_userid " \
          "FROM licitacao " \
          "WHERE comprador_utilizador_userid != %s AND valor < %s" \
          " AND leilao_leilaoid = %s AND valida = true"

    try:
        values = (compradorId, licitacao, leilaoId)
        cur.execute(sql, values)
        rows = cur.fetchall()
        if len(rows) == 0:
            codigoErro = '020'
            return jsonify(erro=codigoErro)

        for row in rows: # para cada comprador que foi superado o seu valor, escrever uma msg no seu inbox
            idUser = row[0]
            sqlQuery = "INSERT INTO notificacao (comentario, momento, utilizador_userid) " \
                       "VALUES (%s, NOW() + INTERVAL '1 hours', %s)"

            try:
                comentario = f"Licitacao ultrapassadda pelo user {compradorId}, com o valor de {licitacao}"
                values = (comentario, idUser)
                cur.execute(sqlQuery, values)
                cur.execute("commit")
                sucess = True

                content = {'Comprador ID': compradorId, 'Valor Licitacao': licitacao, 'Leilao ID':leilaoId}
                payload.append(content)

            except (Exception, psycopg2.DatabaseError) as error:
                logger.error(error)
                sucess = False
                codigoErro = '999'  # Erro nao identificado

    except (Exception, ValueError) as error:
        codigoErro = '003'
        return jsonify(erro=codigoErro)
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999'
        return jsonify(erro=codigoErro)
    finally:
        if conn is not None:
            conn.close()

        if sucess:
            return jsonify(payload)
        else:
            return jsonify(erro=codigoErro)




@app.route("/dbproj/licitar/<leilaoId>/<licitacao>", methods=['GET'])
def make_bidding(leilaoId, licitacao):
    logger.info("###              BD [Make bidding]: GET /dbproj/licitar/<leilaoId>/<licitacao>             ###");
    logger.debug(f'leilaoId: {leilaoId}, licitacao: {licitacao}')

    headers = request.headers
    authCode = headers["authToken"]

    compradorId = getCompradorIdByAuthCode(authCode)
    if (compradorId[0] == None):
        return jsonify(erro=compradorId[1])
    compradorId = compradorId[0]

    try:
        leilaoId = int(leilaoId)
        licitacao = int(licitacao)
    except (Exception, ValueError) as error:
        codigoErro = '003'
        return jsonify(erro=codigoErro)

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT precominimo, maiorlicitacao, vendedor_utilizador_userid"
                " FROM leilao WHERE admincancelou IS NULL AND datafim > (NOW() + INTERVAL '1 hours') "
                "and leilaoid = %s", (leilaoId,) )
    rows = cur.fetchall()

    if len(rows) == 0:
        conn.close()
        codigoErro = '007'
        return jsonify(erro=codigoErro)

    row = rows[0]
    if row[2] == compradorId:
        conn.close()
        codigoErro = '015'
        return jsonify(erro=codigoErro)

    if licitacao < row[0] or licitacao <= row[1]:
        conn.close()
        codigoErro = '012'
        return jsonify(erro=codigoErro)

    try:
        sql = "UPDATE leilao " \
              "SET maiorlicitacao = %s" \
              "WHERE leilaoid = %s "
        values = (licitacao, leilaoId)
        cur.execute(sql, values)

        sql = "INSERT INTO licitacao (valor, momento, comprador_utilizador_userid, leilao_leilaoid)" \
              "VALUES (%s,  %s,  %s,  %s)"
        values = (licitacao, datetime.datetime.now(), compradorId, leilaoId)
        cur.execute(sql, values)

        cur.execute("commit")

        higherBidNotification(compradorId, licitacao, leilaoId)
    except (Exception, psycopg2.DatabaseError) as error:
        conn.close()
        codigoErro = '999'
        return str(error)

    conn.close()
    return jsonify("Sucesso")


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
    headers = request.headers
    authCode = headers["authToken"]

    adminID = getAdminIdByAuthCode(authCode)
    userID = getUserIdByAuthCode(payload['userID'])


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
        values = (adminID, userID)
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
        values = userID
        cur.execute(sql, values)
        rows = cur.fetchall()

        if len(rows) == 0: # Significa que nao esta a vender nada atualmente
            codigoErro = '008' # User nao tem leiloes a decorrer

        else: # Significa que tem leiloes ativos e temos de as cancelar
            sql = "UPDATE leilao " \
                  "SET admincancelou = %s " \
                  "WHERE vendedor_utilizador_userid = %s"

            values = (adminID, userID)
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

    values = userID
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
        values = userID
        cur.execute(sql ,values)
        rows = cur.fetchall()

        for row in rows: #Vou percorrer cada leilao que ele pertence para modificar as licitacoes
            leilaoID = row[0]
            logger.debug(f'LEILAO ID: {leilaoID}, TYPE: {type(leilaoID)}')

            sqlQuery = "SELECT MAX(valor) FROM licitacao WHERE comprador_utilizador_userid = %s and leilao_leilaoid = %s "
            sqlValues = (userID, leilaoID)
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
                        "VALUES (%s, NOW() + INTERVAL '1 hours', %s , %s)"

            try:
                comentario = f"Lamentamos o incomodo mas o utilizador {userID} foi banido do leilao {leilaoID}"
                values = (comentario, userID, leilaoID)
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

            comentario = f"Utilizador {userID} foi banido do leilao {leilaoID}"
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


@app.route("/dbproj/cancelarLeilao/<leilaoId>", methods=['PUT'], strict_slashes=True)
def cancel_auction(leilaoId):
    logger.info("###              BD [Cancel auction]: GET /dbproj/cancelarLeilao/<leilaoId>             ###");
    logger.debug(f'leilaoId: {leilaoId}')

    headers = request.headers
    authCode = headers["authToken"]

    adminId = getAdminIdByAuthCode(authCode)
    if (adminId[0] == None):
        return jsonify(erro=adminId[1])
    adminId = adminId[0]

    try:
        leilaoId = int(leilaoId)
    except (Exception, ValueError) as error:
        codigoErro = '003'
        return jsonify(erro=codigoErro)

    conn = db_connection()
    cur = conn.cursor()

    cur.execute("SELECT leilaoid FROM leilao "
                "WHERE admincancelou IS NULL AND datafim > (NOW() + INTERVAL '1 hours') AND leilaoid = %s"
                , (leilaoId,))
    rows = cur.fetchall()
    if len(rows) == 0:
        conn.close()
        codigoErro = '007'
        return jsonify(erro=codigoErro)

    cur.execute("UPDATE leilao SET admincancelou = %s WHERE leilaoid = %s", (adminId, leilaoId))

    cur.execute("commit")
    conn.close()
    return jsonify(leilaoId=leilaoId)


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


@app.route("/dbproj/msgMural/<leilao_leilaoid>", methods=['POST'])
def sendMsgAuction(leilao_leilaoid):
    logger.info("###              BD [PUT Auction]: POST /dbproj/msgMural/<leilao_leilaoid>              ###");

    headers = request.headers
    payload = request.get_json()

    try:
        leilaoId = checkLeilaoAtivo(leilao_leilaoid)
        if (leilaoId[0] == None):
            return jsonify(erro=leilaoId[1])
        leilaoId = leilaoId[0]
        # leilaoId = int(leilao_leilaoid)
        authCode = headers['authToken']
        msg = payload['mensagem']
        if(len(msg) > 512):
            codigoErro = '003'
            return jsonify(erro=codigoErro)
    except (Exception, ValueError) as error:
        codigoErro = '003'
        return jsonify(erro=codigoErro)

    userId = getUserIdByAuthCode(authCode)
    if (userId[0] == None):
        return jsonify(erro=userId[1])
    userId = userId[0]
    #return jsonify(leilaoId=leilaoId, userId=userId, msg=msg) # DEBUG

    statement = """INSERT INTO mensagem (comentario, momento, utilizador_userid, leilao_leilaoid) 
                          VALUES ( %s, (NOW() + INTERVAL '1 hours'), %s, %s) RETURNING id"""

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- new msg  ----")
    logger.debug(f'payload: {payload}')

    try:
        cur.execute(statement, (msg, userId, leilaoId,))
        sucess = True
        novaMsgId = int(cur.fetchone()[0])
        cur.execute("commit")
    except psycopg2.IntegrityError:
        sucess = False
        codigoErro = '007'  # Leilao Inexistente
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        sucess = False
        codigoErro = '999'  # Erro nao identificado
    finally:
        if conn is not None:
            conn.close()
    if (sucess):
        return jsonify(mensagemId=novaMsgId)
    else:
        return jsonify(erro=codigoErro)


@app.route("/dbproj/caixaEntrada", methods=['GET'], strict_slashes=True)
def get_inbox():
    logger.info("###              BD [Get Inbox By User]: Get /dbproj/caixaEntrada              ###");

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

    cur.execute("SELECT leilao_leilaoid, comentario, momento FROM notificacao WHERE utilizador_userid = %s", (userId,))
    rows = cur.fetchall()
    for row in rows:
        #"LeilaoId": 7, "Aviso": “Licitação ultrapassada.”, "Momento": "2021-05-27 19:13:49"
        content = {'LeilaoId': row[0], 'Aviso': row[1], 'Momento': row[2]}
        payload.append(content)  # appending to the payload to be returned
        
    
    cur.execute("SELECT username, leilao_leilaoid, comentario, momento FROM mensagem, utilizador "
                "WHERE utilizador_userid = userid AND utilizador_userid != %s "
                "AND leilao_leilaoid IN (SELECT leilao_leilaoid FROM mensagem WHERE utilizador_userid = %s) "
                "ORDER BY momento DESC"
                , (userId, userId))
    rows = cur.fetchall()
    payload = []
    for row in rows:
        #“Username”: “User1”, "LeilaoId": 2, "Momento": "2021-05-27 11:17:54", "Comentario": “oi”
        content = {'Username': row[0], 'LeilaoId': row[1], 'Comentario': row[2], 'Momento': row[3]}
        payload.append(content)  # appending to the payload to be returned


    return jsonify(payload)


def checkLeilaoAtivo(idLeilao):
    leilao = None
    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT leilaoid FROM leilao WHERE leilaoid = %s AND admincancelou IS NULL AND datafim > (NOW() + INTERVAL '1 hours')", (idLeilao,))
        rows = cur.fetchall()
        if (len(rows) != 1):
            codigoErro = '007'  # Leilão inativo/inexistente
            return (None, codigoErro)
        leilao = rows[0]
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999'  # Erro nao identificado
        return (None, codigoErro)
    finally:
        if conn is not None:
            conn.close()
    return leilao

@app.route("/dbproj/adminStats", methods=['GET'])
def getAdminStats():
    logger.info("###              BD [GET AdminStats]: Get /dbproj/msgMural/<leilao_leilaoid>              ###");

    headers = request.headers
    try:
        authCode = headers['authToken']
    except (Exception, ValueError) as error:
        codigoErro = '003'  # Input Invalido
        return jsonify(erro=codigoErro)

    adminId = getUserIdByAuthCode(authCode)
    if (adminId[0] == None):
        return jsonify(erro=adminId[1])
    adminId = adminId[0]

    resposta = []

    # TOP 10 UTILIZADORES COM MAIS LEILÕES CRIADOS
    conn = db_connection()
    cur = conn.cursor()
    try:
        cur.execute("SELECT userid, username, COUNT(leilao.leilaoid) FROM utilizador, leilao" \
                    " WHERE utilizador.userid = leilao.vendedor_utilizador_userid" \
                    " GROUP BY userid, username ORDER BY COUNT DESC")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify(erro='999')

    rows = cur.fetchall()

    aux = []
    count = 0
    logger.debug("---- Top 10 Utilizadores com mais leiloes criados  ----")
    for row in rows:
        if count == 10:
            break
        logger.debug(row)
        content = {'userId': int(row[0]), 'Username': row[1], 'Leiloes Criados' : int(row[2])}
        aux.append(content)  # appending to the payload to be returned
        count += 1
    aux.insert(0, "Top " + str(count) + " Utilizadores com mais leiloes criados")
    resposta.append(aux)

    # TOP 10 UTILIZADORES QUE MAIS LEILÕES VENCERAM
    try:
        cur.execute("SELECT userid, username, COUNT(leilao.leilaoid) FROM utilizador, leilao, licitacao" \
                    " WHERE leilao.maiorlicitacao = licitacao.valor AND leilao.leilaoid = licitacao.leilao_leilaoid" \
                    " AND licitacao.comprador_utilizador_userid = utilizador.userid" \
                    " AND licitacao.valida = TRUE AND admincancelou IS NULL" \
                    " AND leilao.datafim < (NOW() + INTERVAL '1 hours')" \
                    " GROUP BY userid, username ORDER BY COUNT DESC")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify(erro='999')

    rows = cur.fetchall()
    aux = []
    count = 0
    logger.debug("---- Top 10 Utilizadores que mais leiloes venceram  ----")
    for row in rows:
        if count == 10:
            break
        logger.debug(row)
        content = {'userId': int(row[0]), 'Username': row[1], 'Leiloes Vencidos' : int(row[2])}
        aux.append(content)  # appending to the payload to be returned
        count += 1
    aux.insert(0, "Top " + str(count) + " Utilizadores que mais leiloes venceram")
    resposta.append(aux)

    # NÚMERO TOTAL DE LEILÕES NOS ÚLTIMOS 10 DIAS
    try:
        cur.execute("SELECT COUNT(leilaoid) FROM leilao WHERE datafim > (NOW() - INTERVAL '-1 hour 10 days')")
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify(erro='999')
    rows = cur.fetchall()
    logger.debug("---- Numero total de leiloes nos ultimos 10 dias  ----")
    logger.debug(rows)
    content = {'Numero total de leiloes nos ultimos 10 dias': int(rows[0][0])}
    resposta.append(content)
    if conn is not None:
        conn.close()

    return jsonify(resposta)

@app.route("/dbproj/versoes/<leilaoid>", methods=['GET'])
def getVersoesLeilao(leilaoid):
    logger.info("###              BD [GET OLD AUCTION VERSIONS]: GET /dbproj/versoes/<leilaoid>              ###")

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT versaoid, titulo, descricao FROM versao WHERE leilao_leilaoid = %s", (leilaoid,))
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return jsonify(erro='999')

    rows = cur.fetchall()

    payload = []
    logger.debug("---- Versoes Leiloes  ----")
    for row in rows:
        logger.debug(row)
        content = {'versaoId': int(row[0]), 'titulo': row[1], 'descricao': row[2]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
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

def getAdminIdByAuthCode(authCode):
    adminId = None

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT utilizador_userid FROM administrador, utilizador  WHERE authToken = %s AND utilizador_userid = userid", (authCode,))
        rows = cur.fetchall()
        if(len(rows) != 1):
            codigoErro = '011'  # Utilizador nao e um admin/não existe
            return (None, codigoErro)
        adminId = rows[0]
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999'  # Erro nao identificado
        return (None, codigoErro)
    finally:
        if conn is not None:
            conn.close()

    return adminId


def getCompradorIdByAuthCode(authCode):
    compradorId = None

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT utilizador_userid FROM comprador, utilizador  WHERE authToken = %s AND utilizador_userid = userid", (authCode,))
        rows = cur.fetchall()
        if(len(rows) != 1):
            codigoErro = '014'  # Utilizador nao e um comprador/não existe
            return (None, codigoErro)
        compradorId = rows[0]
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999'  # Erro nao identificado
        return (None, codigoErro)
    finally:
        if conn is not None:
            conn.close()

    return compradorId

def getVendedorIdByAuthCode(authCode):
    vendedorId = None

    conn = db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT utilizador_userid FROM vendedor, utilizador  WHERE authToken = %s AND utilizador_userid = userid", (authCode,))
        rows = cur.fetchall()
        if(len(rows) != 1):
            codigoErro = '014'  # Utilizador nao e um comprador/não existe
            return (None, codigoErro)
        vendedorId = rows[0]
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        codigoErro = '999'  # Erro nao identificado
        return (None, codigoErro)
    finally:
        if conn is not None:
            conn.close()

    return vendedorId


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
