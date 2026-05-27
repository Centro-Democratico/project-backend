#!/bin/bash
set -e

echo "Clonando repositorio..."
git clone https://github.com/Centro-Democratico/project-backend.git
cd project-backend
git fetch origin
git checkout Tutorial

echo "Creando archivo .env..."
cp .env.example .env

echo "Levantando base de datos PostgreSQL..."
cd scripts
sudo docker-compose --env-file ../.env up -d
cd ..

echo "Esperando que PostgreSQL inicie..."
sleep 5

echo "Creando entorno virtual..."
python3 -m venv venv

echo "Instalando dependencias..."
venv/bin/pip install -r requirements.txt

echo "Aplicando migraciones..."
venv/bin/python manage.py migrate

echo "Ejecutando pruebas..."
venv/bin/python manage.py test
