# 
# Bases de Dados 2020/2021
# Trabalho Prático
#
# Trabalho realizado por:
#    Diogo Filipe    | uc2018288391@student.uc.pt
#    José Gomes      | uc2018286225@student.uc.pt
#    Pedro Marques   | uc2018285632@student.uc.pt

FROM library/postgres


ENV POSTGRES_USER aulaspl
ENV POSTGRES_PASSWORD aulaspl
ENV POSTGRES_DB bdLeiloes

COPY BD2021Leiloes.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
