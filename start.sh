#!/bin/bash

BASE="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$BASE/project-backend"
FRONTEND="$BASE/project-frontend"

# Verificar que el setup se haya ejecutado
if [ ! -d "$BACKEND/.venv" ]; then
    echo "[ERROR] No se encontro el entorno virtual del backend."
    echo "        Ejecuta ./setup.sh primero."
    exit 1
fi

if [ ! -d "$FRONTEND/node_modules" ]; then
    echo "[ERROR] No se encontraron las dependencias del frontend."
    echo "        Ejecuta ./setup.sh primero."
    exit 1
fi

echo "================================================"
echo " Arrancando servidores..."
echo " Backend:  http://localhost:8000"
echo " Frontend: http://localhost:5173"
echo "================================================"
echo

# Arrancar backend en background
cd "$BACKEND"
source .venv/bin/activate
python manage.py runserver &
BACKEND_PID=$!

# Esperar a que Django arranque
sleep 3

# Arrancar frontend en background
cd "$FRONTEND"
npm run dev &
FRONTEND_PID=$!

# Esperar y abrir navegador
sleep 5
if command -v xdg-open &> /dev/null; then
    xdg-open http://localhost:5173    # Linux
elif command -v open &> /dev/null; then
    open http://localhost:5173         # Mac
fi

echo
echo " Servidores corriendo. Presiona Ctrl+C para detener todo."
echo

# Al presionar Ctrl+C detiene ambos procesos
trap "kill $BACKEND_PID $FRONTEND_PID; echo 'Servidores detenidos.'; exit 0" SIGINT
wait
