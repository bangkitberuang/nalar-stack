#!/bin/bash
set -e

# Deteksi docker compose v2 atau v1
if docker compose version >/dev/null 2>&1; then
    DC="docker compose"
elif command -v docker-compose >/dev/null 2>&1; then
    DC="docker-compose"
else
    echo "[ERROR] Docker Compose belum terpasang. Install Docker terlebih dahulu."
    exit 1
fi

echo "=================================================="
echo "    Memulai Deployment NALAR AI Coding Harness    "
echo "=================================================="

# 1. Pastikan file .env ada & generate secret acak yang aman
if [ ! -f .env ]; then
    echo "[*] Membuat file .env dari template..."
    cp .env.example .env

    JWT_RAND=$(openssl rand -hex 32)
    SESS_RAND=$(openssl rand -hex 32)
    ENC_RAND=$(openssl rand -hex 32)

    sed -i "s/^JWT_SECRET=.*/JWT_SECRET=$JWT_RAND/" .env
    sed -i "s/^SESSION_SECRET=.*/SESSION_SECRET=$SESS_RAND/" .env
    sed -i "s/^STORAGE_ENCRYPTION_KEY=.*/STORAGE_ENCRYPTION_KEY=$ENC_RAND/" .env
    echo "[+] Secrets acak (64-char) berhasil digenerate."
fi

# Load variables
set -a
source .env
set +a

# 2. Cek users_database.yml
if [ ! -f authelia/config/users_database.yml ]; then
    echo "[!] File authelia/config/users_database.yml belum ditemukan!"
    echo "    Jalankan perintah berikut dulu:"
    echo "    cp authelia/config/users_database.yml.example authelia/config/users_database.yml"
    echo "    docker run --rm -it authelia/authelia:4.38 authelia crypto hash generate argon2"
    echo "    Lalu paste hasil Digest ke authelia/config/users_database.yml dan jalankan ./deploy.sh lagi."
    exit 1
fi

# 3. Buat folder project & dummy SSL agar Nginx bisa start pertama kali
mkdir -p "$HOST_PROJECTS_DIR"
mkdir -p "certbot/conf/live/$NALAR_SUBDOMAIN"
mkdir -p "certbot/www"

USING_DUMMY=0
if [ ! -f "certbot/conf/live/$NALAR_SUBDOMAIN/fullchain.pem" ]; then
    echo "[*] Menyiapkan sertifikat dummy SSL sementara untuk inisialisasi Nginx..."
    openssl req -x509 -nodes -newkey rsa:2048 -days 1 \
        -keyout "certbot/conf/live/$NALAR_SUBDOMAIN/privkey.pem" \
        -out "certbot/conf/live/$NALAR_SUBDOMAIN/fullchain.pem" \
        -subj "/CN=localhost" 2>/dev/null
    USING_DUMMY=1
fi

# 4. Build dan jalankan container
echo "[*] Membangun image NALAR dan menyalakan container..."
$DC up -d --build

# 5. Request SSL resmi Let's Encrypt (mengganti dummy cert)
if [ "$USING_DUMMY" -eq 1 ]; then
    echo "[*] Menghapus dummy cert dan mengajukan SSL resmi Let's Encrypt..."
    rm -rf "certbot/conf/live/$NALAR_SUBDOMAIN"
    $DC run --rm --entrypoint "" certbot certbot certonly \
        --webroot --webroot-path /var/www/certbot \
        --cert-name "$NALAR_SUBDOMAIN" \
        -d "$NALAR_SUBDOMAIN" -d "$AUTH_SUBDOMAIN" \
        --email "$EMAIL_LETSENCRYPT" --agree-tos --no-eff-email || {
            echo "[!] Certbot gagal. Pastikan DNS A-Record $NALAR_SUBDOMAIN dan $AUTH_SUBDOMAIN sudah mengarah ke IP VPS ini, lalu jalankan ulang ./deploy.sh."
            exit 1
        }
    $DC exec nginx nginx -s reload
fi

echo "=================================================="
echo " [OK] NALAR Berhasil Dijalankan!"
echo " 1. Login & daftar 2FA : https://$AUTH_SUBDOMAIN"
echo " 2. Buka NALAR         : https://$NALAR_SUBDOMAIN"
echo "=================================================="
