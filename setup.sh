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
for cmd in git python3 node npm docker; do
    if ! command -v $cmd &> /dev/null; then
        echo "[ERROR] '$cmd' no esta instalado."
        exit 1
    fi
done
echo "[OK] Dependencias verificadas."
echo

# ------------------------------------------------
# 2. Clonar o actualizar repositorios
# ------------------------------------------------
if [ ! -d "$BACKEND" ]; then
    echo "[1/5] Clonando backend..."
    git clone https://github.com/Centro-Democratico/project-backend.git "$BACKEND"
else
    echo "[1/5] Backend ya existe, actualizando..."
    cd "$BACKEND" && git pull
fi

if [ ! -d "$FRONTEND" ]; then
    echo "[2/5] Clonando frontend..."
    git clone https://github.com/Centro-Democratico/project-frontend.git "$FRONTEND"
else
    echo "[2/5] Frontend ya existe, actualizando..."
    cd "$FRONTEND" && git pull
fi

# ------------------------------------------------
# 3. Levantar base de datos con Docker
# ------------------------------------------------
echo "[3/5] Levantando base de datos con Docker..."
cd "$BASE"
docker compose up -d db

echo "    Esperando a que PostgreSQL este listo..."
sleep 5

# ------------------------------------------------
# 4. Configurar backend
# ------------------------------------------------
echo "[4/5] Configurando backend..."
cd "$BACKEND"

if [ ! -d ".venv" ]; then
    echo "    Creando entorno virtual..."
    python3 -m venv .venv
fi

# Generar .env con credenciales de Docker
cat > .env << 'ENVEOF'
DB_HOST=localhost
DB_PORT=5432
DB_USER=benchmark_user
DB_PASSWORD=benchmark_pass
DB_NAME=benchmark_db
ENV=development
ENVEOF
echo "    .env generado correctamente."

source .venv/bin/activate
pip install -r requirements.txt --quiet
python manage.py migrate --run-syncdb

# ------------------------------------------------
# 5. Configurar frontend
# ------------------------------------------------
echo "[5/5] Configurando frontend..."
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
