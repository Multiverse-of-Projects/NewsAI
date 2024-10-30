#!/bin/bash
set -e

mongoimport --db NewAI --collection News_Articles --file /docker-entrypoint-initdb.d/data/NewAI.News_Articles.json --jsonArray
mongoimport --db NewAI --collection News_Articles_Ids --file /docker-entrypoint-initdb.d/data/NewAI.News_Articles_Ids.json --jsonArray