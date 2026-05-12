@echo off
REM --------------------------------------
REM Script de preparación inicial del proyecto (Windows)
REM --------------------------------------

REM 1. Clonar repositorio y cambiar a rama Tutorial
echo Clonando repositorio...
git clone https://github.com/Centro-Democratico/project-backend.git
cd project-backend
git fetch origin
git checkout Tutorial

REM 2. Configurar variables de entorno
echo Creando archivo .env...
copy .env.example .env

REM 3. Levantar base de datos con Docker
echo Levantando base de datos PostgreSQL...
cd scripts
docker-compose --env-file ..\.env up -d
cd ..

REM 4. Preparar entorno Python
echo Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate
pip install -r requirements.txt

REM 5. Ejecutar pruebas básicas
echo Ejecutando pruebas...
python manage.py test
