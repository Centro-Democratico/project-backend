@echo off
echo Iniciando backend...
start cmd /k "cd project-backend && .venv\Scripts\activate && python manage.py runserver"

echo Iniciando frontend...
start cmd /k "cd project-frontend && npm run dev"

echo Ambos servidores corriendo.
