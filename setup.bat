@echo off
echo Clonando repositorio...
git clone https://github.com/Centro-Democratico/project-backend.git
cd project-backend
git fetch origin
git checkout Tutorial

echo Creando archivo .env...
copy .env.example .env

echo Levantando base de datos PostgreSQL...
cd scripts
docker-compose --env-file ..\.env up -d
cd ..

echo Esperando que PostgreSQL inicie...
timeout /t 5 /nobreak

echo Creando entorno virtual...
python -m venv venv

echo Instalando dependencias...
venv\Scripts\pip install -r requirements.txt

echo Aplicando migraciones...
venv\Scripts\python manage.py migrate

echo Ejecutando pruebas...
venv\Scripts\python manage.py test
