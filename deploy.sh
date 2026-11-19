#!/bin/bash
set -e

if docker compose version >/dev/null 2>&1; then
    DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
else
    echo "[ERROR] Docker Compose belum terpasang."
    exit 1
fi

echo "=================================================="
echo "   Deployment NALAR AI Coding Harness (Traefik)   "
echo "=================================================="

# 1. Generate .env & random 64-char secrets jika belum ada
if [ ! -f .env ]; then
    echo "[*] Membuat .env dengan secrets acak..."
    cp .env.example .env

    JWT_RAND=$(openssl rand -hex 32)
    SESS_RAND=$(openssl rand -hex 32)
    ENC_RAND=$(openssl rand -hex 32)

    sed -i "s/^JWT_SECRET=.*/JWT_SECRET=$JWT_RAND/" .env
    sed -i "s/^SESSION_SECRET=.*/SESSION_SECRET=$SESS_RAND/" .env
    sed -i "s/^STORAGE_ENCRYPTION_KEY=.*/STORAGE_ENCRYPTION_KEY=$ENC_RAND/" .env
fi

set -a
source .env
set +a

# 2. Pastikan users_database.yml sudah ada
if [ ! -f authelia/config/users_database.yml ]; then
    echo "[!] File authelia/config/users_database.yml belum dibuat!"
    echo "    Jalankan:"
    echo "    cp authelia/config/users_database.yml.example authelia/config/users_database.yml"
    echo "    docker run --rm -it authelia/authelia:4.38 authelia crypto hash generate argon2"
    exit 1
fi

# 3. Pasang konfigurasi routing Traefik Coolify (hot-reload otomatis, zero downtime)
TRAEFIK_DIR="${TRAEFIK_DYNAMIC_DIR:-/data/coolify/proxy/dynamic}"
if [ -d "$TRAEFIK_DIR" ]; then
    echo "[*] Memasang konfigurasi Traefik ke $TRAEFIK_DIR/nalar.yaml ..."
    cp traefik/nalar.yaml "$TRAEFIK_DIR/nalar.yaml"
else
    echo "[!] Peringatan: Direktori $TRAEFIK_DIR tidak ditemukan. Copy traefik/nalar.yaml manual."
fi

# 4. Build & start container NALAR + Authelia
echo "[*] Membangun image NALAR dan menyalakan container..."
$DC up -d --build

echo "=================================================="
echo " [OK] NALAR Berhasil Dijalankan!"
echo " Portal 2FA : https://$AUTH_SUBDOMAIN"
echo " Dashboard  : https://$NALAR_SUBDOMAIN"
echo "=================================================="
