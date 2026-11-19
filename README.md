# NALAR AI Coding Harness (Self-Hosted on Docker)
*Personal AI agent harness with Google Authenticator (TOTP) 2FA protection*

Stack:
- **NALAR Engine** (Custom-branded T3 Code Agent Control Plane)
- **Authelia** (TOTP 2FA Authenticator portal)
- **Nginx Reverse Proxy** (SSL termination + WebSocket streaming + Authelia auth_request)

---

## Struktur Direktori
```text
nalar-stack/
├── .env.example
├── .gitignore
├── deploy.sh                  # Script deployment otomatis
├── docker-compose.yml         # Orkestrasi NALAR + Authelia + Nginx
├── Dockerfile.nalar           # Build NALAR dari source dengan branding NALAR
├── authelia/
│   └── config/
│       ├── configuration.yml
│       └── users_database.yml.example
└── nginx/
    └── conf.d/
        └── nalar.conf
```

---

## Cara Deployment di VPS (Cepat & Mudah)

### 1. Upload / Clone ke VPS
Di VPS Linux Anda:
```bash
git clone <URL_REPO_ANDA> ~/nalar-stack
cd ~/nalar-stack
```

### 2. Konfigurasi Environment & Password
Salin file environment:
```bash
cp .env.example .env
cp authelia/config/users_database.yml.example authelia/config/users_database.yml
```

Buat password hash untuk login:
```bash
docker run --rm authelia/authelia:latest authelia crypto hash-password "PasswordRahasiaAnda"
```
Salin hash yang dihasilkan, lalu masukkan ke `authelia/config/users_database.yml` di bagian `password:`.

### 3. Jalankan Script Deploy
```bash
chmod +x deploy.sh
./deploy.sh
```

### 4. Aktivasi Google Authenticator
1. Buka browser HP ke `https://auth.bangkit.io`
2. Login dengan username `admin` dan password Anda.
3. Buka link aktivasi QR code di VPS:
   ```bash
   cat authelia/config/notification.txt
   ```
4. Buka link tersebut di HP dan scan QR Code menggunakan aplikasi **Google Authenticator**.
5. Sekarang Anda bisa mengakses `https://nalar.bangkit.io` dengan aman dari HP!
