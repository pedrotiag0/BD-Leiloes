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
    Diogo Filipe    | <uc2018288391@student.uc.pt><br/>
    José Gomes      | <uc2018286225@student.uc.pt><br/>
    Pedro Marques   | <uc2018285632@student.uc.pt><br/>
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

    # parameterized queries, good for security and performance
    statement = """
                  INSERT INTO Utilizador (username, email, password) 
                          VALUES ( %s,   %s ,   %s )"""

    values = (payload["username"], payload["email"], payload["password"])

    try:
        cur.execute(statement, values)
        cur.execute("commit")
        result = 'Inserted!'    # Tem de ser alterado
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        result = 'Failed!'      # Tem de ser alterado
    finally:
        if conn is not None:
            conn.close()

    return jsonify(result)
