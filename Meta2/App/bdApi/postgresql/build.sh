#!/bin/bash
# 
# Bases de Dados 2020/2021
# Trabalho Prático
#
# Trabalho realizado por:
#    Diogo Filipe    | uc2018288391@student.uc.pt
#    José Gomes      | uc2018286225@student.uc.pt
#    Pedro Marques   | uc2018285632@student.uc.pt

image="bd-psql"
container="db"



echo "-- Building --"
docker   build  -t  $image   .
