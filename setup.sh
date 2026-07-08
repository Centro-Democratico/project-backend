#!/bin/bash
set -e

echo "================================================"
echo "        KnowYourMarks - Setup"
echo "================================================"
echo ""

BASE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND="$BASE/project-backend"
FRONTEND="$BASE/project-frontend"

# ------------------------------------------------
# 1. Verificar dependencias
# ------------------------------------------------
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "[ERROR] $1 no esta instalado. Descargalo en $2"
        exit 1
    fi
}

check_command "git" "https://git-scm.com"
check_command "python3" "https://python.org"
check_command "node" "https://nodejs.org"
check_command "docker" "https://docker.com"

echo "[OK] Dependencias verificadas."
echo ""

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

echo ""

# ------------------------------------------------
# 3. Levantar base de datos con Docker
# ------------------------------------------------
echo "[3/5] Levantando base de datos con Docker..."
cd "$BACKEND"
docker compose up -d db

echo "    Esperando a que PostgreSQL este listo (10 segundos)..."
sleep 10

# --- ¡AQUI AUTOMATIZAMOS EL SCRIPT DE NAEL! ---
if [ -f "scripts/init.sql" ]; then
    echo "    Inyectando init.sql en el contenedor..."
    docker compose exec -T db psql -U postgres < scripts/init.sql
    echo "    [OK] Base de datos y usuario creados desde init.sql."
else
    echo "    [ADVERTENCIA] No se encontro el archivo en scripts/init.sql"
fi
echo ""

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
cat > .env << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_USER=benchmark_user
DB_PASSWORD=benchmark_pass
DB_NAME=benchmark_db
ENV=development
EOF
echo "    .env generado correctamente."

# Activar entorno virtual e instalar dependencias
source .venv/bin/activate
pip install -r requirements.txt --quiet

echo "    Ejecutando migraciones de Django..."
python manage.py migrate --run-syncdb

# ------------------------------------------------
# 5. Configurar frontend
# ------------------------------------------------
echo "[5/5] Configurando frontend..."
cd "$FRONTEND"

if [ ! -f ".env" ]; then
    cp ".env.example" ".env"
    echo "    Archivo .env creado automaticamente para el frontend."
fi

if [ ! -d "node_modules" ]; then
    echo "    Instalando dependencias npm..."
    npm install --silent
fi

echo ""
echo "================================================"
echo "  Setup completado. Ejecuta ./start.sh para"
echo "  arrancar el proyecto."
echo "================================================"
echo ""
