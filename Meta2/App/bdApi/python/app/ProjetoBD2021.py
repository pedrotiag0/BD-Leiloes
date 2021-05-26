from flask import Flask, jsonify, request
import logging, psycopg2, time

app = Flask(__name__)


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
