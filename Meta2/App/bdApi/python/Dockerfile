# 
# Bases de Dados 2020/2021
# Trabalho Prático
#
# Trabalho realizado por:
#    Diogo Filipe    | uc2018288391@student.uc.pt
#    José Gomes      | uc2018286225@student.uc.pt
#    Pedro Marques   | uc2018285632@student.uc.pt

from python:3.9-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

run pip install flask

run pip install pyjwt

run pip install passlib

run pip install psycopg2-binary

copy . /app

volume ["/app"]

workdir /app

run mkdir -p logs

EXPOSE 5000

CMD ["python", "ProjetoBD2021.py"]
