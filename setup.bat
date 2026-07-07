@echo off
setlocal enabledelayedexpansion

echo ================================================
echo        KnowYourMarks - Setup
echo ================================================
echo.

set BASE=%~dp0
set BACKEND=%BASE%project-backend
set FRONTEND=%BASE%project-frontend

:: ------------------------------------------------
:: 1. Verificar dependencias
:: ------------------------------------------------
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Git no esta instalado. Descargalo en https://git-scm.com
    pause & exit /b 1
)

where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado. Descargalo en https://python.org
    pause & exit /b 1
)

where node >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js no esta instalado. Descargalo en https://nodejs.org
    pause & exit /b 1
)

where docker >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta instalado. Descargalo en https://docker.com
    pause & exit /b 1
)

echo [OK] Dependencias verificadas.
echo.

:: ------------------------------------------------
:: 2. Clonar o actualizar repositorios
:: ------------------------------------------------
if not exist "%BACKEND%" (
    echo [1/5] Clonando backend...
    git clone https://github.com/Centro-Democratico/project-backend.git "%BACKEND%"
) else (
    echo [1/5] Backend ya existe, actualizando...
    cd /d "%BACKEND%" && git pull
)

if not exist "%FRONTEND%" (
    echo [2/5] Clonando frontend...
    git clone https://github.com/Centro-Democratico/project-frontend.git "%FRONTEND%"
) else (
    echo [2/5] Frontend ya existe, actualizando...
    cd /d "%FRONTEND%" && git pull
)

:: ------------------------------------------------
:: 3. Levantar base de datos con Docker
:: ------------------------------------------------
echo [3/5] Levantando base de datos con Docker...
cd /d "%BASE%"
docker compose up -d db

echo     Esperando a que PostgreSQL este listo...
timeout /t 5 /nobreak >nul

:: ------------------------------------------------
:: 4. Configurar backend
:: ------------------------------------------------
echo [4/5] Configurando backend...
cd /d "%BACKEND%"

if not exist ".venv" (
    echo     Creando entorno virtual...
    python -m venv .venv
)

:: Generar .env con credenciales de Docker
(
    echo DB_HOST=localhost
    echo DB_PORT=5432
    echo DB_USER=benchmark_user
    echo DB_PASSWORD=benchmark_pass
    echo DB_NAME=benchmark_db
    echo ENV=development
) > .env
echo     .env generado correctamente.

call .venv\Scripts\activate
pip install -r requirements.txt --quiet
python manage.py migrate --run-syncdb

:: ------------------------------------------------
:: 5. Configurar frontend
:: ------------------------------------------------
echo [5/5] Configurando frontend...
cd /d "%FRONTEND%"
:: Crear el archivo .env automáticamente a partir del ejemplo

if not exist ".env" (
    copy ".env.example" ".env"
    echo     Archivo .env creado automaticamente para el frontend.
)
if not exist "node_modules" (
    echo     Instalando dependencias npm...
    npm install --silent
)

echo.
echo ================================================
echo  Setup completado. Ejecuta start.bat para
echo  arrancar el proyecto.
echo ================================================
echo.
pause
endlocal
