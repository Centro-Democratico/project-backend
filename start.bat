@echo off
setlocal

set BASE=%~dp0
set BACKEND=%BASE%
set FRONTEND=%BASE%..\project-frontend

:: Verificar que el setup se haya ejecutado
if not exist "%BACKEND%.venv" (
    echo [ERROR] No se encontro el entorno virtual del backend.
    echo         Ejecuta setup.bat primero.
    pause & exit /b 1
)

if not exist "%FRONTEND%\node_modules" (
    echo [ERROR] No se encontraron las dependencias del frontend.
    echo         Ejecuta setup.bat primero.
    pause & exit /b 1
)

echo ================================================
echo  Arrancando servidores...
echo  Backend:  http://localhost:8000
echo  Frontend: http://localhost:5173
echo ================================================
echo.

start cmd /k "title Backend - Django && cd /d "%BACKEND%" && call .venv\Scripts\activate && python manage.py runserver"
timeout /t 3 /nobreak >nul
start cmd /k "title Frontend - Vite && cd /d "%FRONTEND%" && npm run dev"

timeout /t 5 /nobreak >nul
start http://localhost:5173

endlocal
