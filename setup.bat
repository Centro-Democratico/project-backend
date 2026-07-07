@echo off
setlocal

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

:: ------------------------------------------------
:: 2. Clonar o actualizar repositorios
:: ------------------------------------------------
if not exist "%BACKEND%" (
    echo [1/4] Clonando backend...
    git clone https://github.com/Centro-Democratico/project-backend.git "%BACKEND%"
) else (
    echo [1/4] Backend ya existe, actualizando...
    cd /d "%BACKEND%" && git pull
)

if not exist "%FRONTEND%" (
    echo [2/4] Clonando frontend...
    git clone https://github.com/Centro-Democratico/project-frontend.git "%FRONTEND%"
) else (
    echo [2/4] Frontend ya existe, actualizando...
    cd /d "%FRONTEND%" && git pull
)

:: ------------------------------------------------
:: 3. Configurar backend
:: ------------------------------------------------
echo [3/4] Configurando backend...
cd /d "%BACKEND%"

if not exist ".venv" (
    echo     Creando entorno virtual...
    python -m venv .venv
)

call .venv\Scripts\activate
pip install -r requirements.txt --quiet
python manage.py migrate --run-syncdb

:: ------------------------------------------------
:: 4. Configurar frontend
:: ------------------------------------------------
echo [4/4] Configurando frontend...
cd /d "%FRONTEND%"

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
