#!/bin/bash
# Baixa e instala o driver manualmente para evitar falhas de repositório
curl -O https://download.microsoft.com/download/3/5/5/355d7943-6608-467a-85d0-2384c3116898/msodbcsql18_18.3.3.1-1_amd64.deb
apt-get update
apt-get install -y ./msodbcsql18_18.3.3.1-1_amd64.deb