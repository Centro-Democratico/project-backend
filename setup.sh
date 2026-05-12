#!/bin/bash
# --------------------------------------
# Script de preparación inicial del proyecto (Linux/Mac/WSL)
# --------------------------------------

# 1. Clonar repositorio y cambiar a rama Tutorial
echo "Clonando repositorio..."
git clone https://github.com/Centro-Democratico/project-backend.git
cd project-backend
git fetch origin
git checkout Tutorial

# 2. Configurar variables de entorno
echo "Creando archivo .env..."
cp .env.example .env

# 3. Levantar base de datos con Docker
echo "Levantando base de datos PostgreSQL..."
cd scripts
sudo docker-compose --env-file ../.env up -d
cd ..

# 4. Preparar entorno Python
echo "Creando entorno virtual..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 5. Ejecutar pruebas básicas
echo "Ejecutando pruebas..."
python manage.py test
