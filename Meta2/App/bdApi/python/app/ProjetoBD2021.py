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

    if not ((32>=len(values[0])>0) and (64>=len(values[1])>0) and (32>=len(values[2])>0)):
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
    if(sucess):
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

    cur.execute("SELECT userid FROM utilizador WHERE username = %s and password = %s", (username,password))
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
        payload.append(content)                                                                     # appending to the payload to be returned

    conn.close()
    return jsonify(payload)


@app.route("/dbproj/leilao", methods=['POST'])
def criaLeilao():
    logger.info("###              BD [Insert Auction]: POST /dbproj/leilao              ###");
    payload = request.get_json()

    conn = db_connection()
    cur = conn.cursor()

    logger.info("---- New Action  ----")
    logger.debug(f'payload: {payload}')

    # parameterized queries, good for security and performance
    # TODO
    # Antes de adicionar à BD tenho de verificar se o ID_VENDEDOR é valido
    statement = """
                  INSERT INTO leilao (precominimo, titulo, descricao, datafim, artigoid, nomeartigo, descricaoartigo, vendedor_utilizador_userid) 
                          VALUES ( %s,   %s ,   %s ,  %s , %s , %s , %s, %s) RETURNING leilaoid """

    values = (
        payload["leilaoPrecoMinimo"], payload["leilaoTitulo"], payload["leilaoDescricao"], payload["leilaoDataFim"],
        payload["artigoId"], payload["nomeArtigo"], payload["descricaoArtigo"], payload["vendedorID"])

    try:
        cur.execute(statement, values)
        sucess = True
        leilaoID = str(cur.fetchone()[0])
        cur.execute("commit")
        #result = 'Auction Created!'  # Tem de ser alterado
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        sucess = False
        #result = 'Failed to create an auction'  # Tem de ser alterado
    finally:
        if conn is not None:
            conn.close()

    if sucess:
        return jsonify(leilaoId=leilaoID)
    else:
        return jsonify(leilaoId='Erro a criar Leilao')



@app.route("/dbproj/leilao/<leilao_leilaoid>", methods=['GET'], strict_slashes=True)
def getDetailsAuction(leilao_leilaoid):
    logger.info("###              BD [Get Auction]: Get /dbproj/leilao/<leilao_leilaoid>              ###");

    conn = db_connection()
    cur = conn.cursor()

    sql = "SELECT leilaoid, titulo, descricao, datafim, artigoid, nomeartigo, descricaoartigo, maiorlicitacao, username " \
          "FROM leilao, utilizador, vendedor WHERE leilaoid = %s AND vendedor_utilizador_userid = userid "

    cur.execute(sql, f'{leilao_leilaoid}')
    rows = cur.fetchall()

    # TODO
    # Falta ir buscar as mesagens do mural - DONE
    # historico de licitacoes - DONE
    payload = []
    logger.debug("---- Auction Details  ----")
    payload.append({"DETALHES DO LEILAO": leilao_leilaoid})
    for row in rows:
        logger.debug(row)
        content = {'leilaoid': int(row[0]), 'titulo': row[1], 'descricao': row[2], 'datafim': row[3],
                   'artigoid': row[4], 'nomeartigo': row[5], 'descricaoartigo': row[6], 'maiorlicitcao': row[7],
                   'username': row[8]}
        payload.append(content)  # appending to the payload to be returned

    sql = "SELECT id, comentario, momento, username " \
          "FROM mensagem, utilizador WHERE leilao_leilaoid = %s AND utilizador_userid = userid "
    cur.execute(sql, f'{leilao_leilaoid}')
    rows = cur.fetchall()

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

    logger.debug("---- Bids Details  ----")
    payload.append({"DETALHES DAS LICITACOES LEILAO": leilao_leilaoid})
    for row in rows:
        logger.debug(row)
        content = {'id': int(row[0]), 'valor': row[1], 'username': row[2]}
        payload.append(content)  # appending to the payload to be returned

    conn.close()
    return jsonify(payload)


def db_connection():
    db = psycopg2.connect(user = "aulaspl",
                            password = "aulaspl",
                            host = "db",
                            port = "5432",
                            database = "bdLeiloes")
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
