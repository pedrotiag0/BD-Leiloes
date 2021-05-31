#!/bin/bash
# 
# Bases de Dados 2020/2021
# Trabalho Prático
#
# Trabalho realizado por:
#    Diogo Filipe    | uc2018288391@student.uc.pt
#    José Gomes      | uc2018286225@student.uc.pt
#    Pedro Marques   | uc2018285632@student.uc.pt


#
# ATTENTION: This will stop and delete all the running containers
# Use it only if you are not using docker for other ativities
#
#docker rm $(docker stop $(docker ps -a -q)) 

mkdir -p python/app/logs

# add  -d  to the command below if you want the containers running in background without logs
docker-compose  -f docker-compose-python-psql.yml up --build