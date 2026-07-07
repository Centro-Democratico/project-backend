#!/bin/bash

echo "================================================"
echo "       KnowYourMarks - Setup"
echo "================================================"
echo

BASE="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$BASE/project-backend"
FRONTEND="$BASE/project-frontend"

# ------------------------------------------------
# 1. Verificar dependencias
# ------------------------------------------------
for cmd in git python3 node npm; do
    if ! command -v $cmd &> /dev/null; then
        echo "[ERROR] '$cmd' no esta instalado."
        exit 1
    fi
done

# ------------------------------------------------
# 2. Clonar o actualizar repositorios
# ------------------------------------------------
if [ ! -d "$BACKEND" ]; then
    echo "[1/4] Clonando backend..."
    git clone https://github.com/Centro-Democratico/project-backend.git "$BACKEND"
else
    echo "[1/4] Backend ya existe, actualizando..."
    cd "$BACKEND" && git pull
fi

if [ ! -d "$FRONTEND" ]; then
    echo "[2/4] Clonando frontend..."
    git clone https://github.com/Centro-Democratico/project-frontend.git "$FRONTEND"
else
    echo "[2/4] Frontend ya existe, actualizando..."
    cd "$FRONTEND" && git pull
fi

# ------------------------------------------------
# 3. Configurar backend
# ------------------------------------------------
echo "[3/4] Configurando backend..."
cd "$BACKEND"

if [ ! -d ".venv" ]; then
    echo "    Creando entorno virtual..."
    python3 -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt --quiet
python manage.py migrate --run-syncdb

# ------------------------------------------------
# 4. Configurar frontend
# ------------------------------------------------
echo "[4/4] Configurando frontend..."
cd "$FRONTEND"

if [ ! -d "node_modules" ]; then
    echo "    Instalando dependencias npm..."
    npm install --silent
fi

echo
echo "================================================"
echo " Setup completado. Ejecuta ./start.sh para"
echo " arrancar el proyecto."
echo "================================================"
echo
