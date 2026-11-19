#!/bin/bash
set -e

echo "=================================================="
echo "    Memulai Deployment NALAR AI Coding Harness    "
echo "=================================================="

# 1. Pastikan file .env ada
if [ ! -f .env ]; then
    echo "[*] Membuat file .env dari template..."
    cp .env.example .env

    # Generate random secrets
    JWT_RAND=$(openssl rand -hex 16)
    SESS_RAND=$(openssl rand -hex 16)
    ENC_RAND=$(openssl rand -hex 16)

    sed -i "s/JWT_SECRET=.*/JWT_SECRET=$JWT_RAND/" .env
    sed -i "s/SESSION_SECRET=.*/SESSION_SECRET=$SESS_RAND/" .env
    sed -i "s/STORAGE_ENCRYPTION_KEY=.*/STORAGE_ENCRYPTION_KEY=$ENC_RAND/" .env
    echo "[+] Secrets baru berhasil digenerate."
fi

# Load variables
source .env

# 2. Pastikan file users_database.yml ada
if [ ! -f authelia/config/users_database.yml ]; then
    echo "[!] File authelia/config/users_database.yml belum ada!"
    echo "[*] Menyalin dari template users_database.yml.example..."
    cp authelia/config/users_database.yml.example authelia/config/users_database.yml
    echo "[!] Silakan atur password admin Anda nanti di: authelia/config/users_database.yml"
fi

# 3. Setup folder certbot & dummy certificate agar Nginx bisa booting awal
mkdir -p certbot/conf/live/$AUTH_SUBDOMAIN
mkdir -p certbot/conf/live/$NALAR_SUBDOMAIN
mkdir -p certbot/www
mkdir -p $HOST_PROJECTS_DIR

if [ ! -f certbot/conf/live/$AUTH_SUBDOMAIN/fullchain.pem ]; then
    echo "[*] Menyiapkan sertifikat dummy SSL sementara untuk inisialisasi Nginx..."
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
        -keyout certbot/conf/live/$AUTH_SUBDOMAIN/privkey.pem \
        -out certbot/conf/live/$AUTH_SUBDOMAIN/fullchain.pem \
        -subj "/CN=localhost" 2>/dev/null
fi

if [ ! -f certbot/conf/live/$NALAR_SUBDOMAIN/fullchain.pem ]; then
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
        -keyout certbot/conf/live/$NALAR_SUBDOMAIN/privkey.pem \
        -out certbot/conf/live/$NALAR_SUBDOMAIN/fullchain.pem \
        -subj "/CN=localhost" 2>/dev/null
fi

# 4. Build dan jalankan container
echo "[*] Membangun dan menjalankan container Docker..."
docker-compose up -d --build

# 5. Minta SSL Asli dari Let's Encrypt jika belum ada
echo "[*] Mengajukan sertifikat SSL resmi (Let's Encrypt)..."
docker-compose run --rm certbot certonly --webroot --webroot-path /var/www/certbot \
    -d $AUTH_SUBDOMAIN -d $NALAR_SUBDOMAIN \
    --email $EMAIL_LETSENCRYPT --agree-tos --no-eff-email --force-renewal || {
        echo "[!] Peringatan: Certbot gagal mengambil SSL Let's Encrypt."
        echo "[!] Pastikan DNS $AUTH_SUBDOMAIN dan $NALAR_SUBDOMAIN sudah mengarah ke IP VPS ini."
    }

# Reload Nginx agar menggunakan sertifikat baru
docker-compose exec nginx nginx -s reload || true

echo "=================================================="
echo " [OK] NALAR Berhasil Dijalankan! "
echo " Portal Auth : https://$AUTH_SUBDOMAIN"
echo " Dashboard   : https://$NALAR_SUBDOMAIN"
echo "=================================================="
