#!/bin/bash
# Instala as dependências necessárias para o pyodbc no Linux
apt-get update
apt-get install -y unixodbc-dev
# Instala o driver da Microsoft (para Debian/Ubuntu, que é a base do App Service Linux)
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql18

# Inicia sua aplicação
gunicorn --bind=0.0.0.0:8000 --timeout 600 config.wsgi