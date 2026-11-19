# NALAR AI Coding Harness (Self-Hosted on Docker)
*Personal AI agent harness dengan proteksi Google Authenticator (TOTP) 2FA*

Stack:
- **NALAR Engine** (Custom-branded `pingdotgg/t3code` Agent Control Plane)
- **Authelia v4.38** (Portal login 2FA / Google Authenticator TOTP)
- **Nginx Reverse Proxy** (HTTPS + WebSocket streaming + Authelia `auth_request`)
- **Certbot** (SSL Let's Encrypt otomatis & auto-renew)

---

## Langkah Deployment di VPS

### 1. Siapkan DNS (Panel Domain `bangkit.io`)
Tambahkan 2 A-Record menuju IP publik VPS Anda:
- `nalar` -> `IP_VPS_ANDA`
- `auth` -> `IP_VPS_ANDA`

### 2. Clone Repo di VPS
```bash
git clone <URL_REPO_ANDA> ~/nalar-stack
cd ~/nalar-stack
```

### 3. Buat User & Password Admin
```bash
cp authelia/config/users_database.yml.example authelia/config/users_database.yml
docker run --rm -it authelia/authelia:4.38 authelia crypto hash generate argon2
```
Salin teks setelah `Digest:` (mulai dari `$argon2id$...`), lalu tempel ke baris `password:` di `authelia/config/users_database.yml`.

### 4. Jalankan Deploy Otomatis
```bash
chmod +x deploy.sh
./deploy.sh
```

### 5. Daftar Google Authenticator di HP
1. Buka `https://auth.bangkit.io` di HP, login dengan user `admin` + password Anda.
2. Di terminal VPS, ambil link aktivasi QR Code:
   ```bash
   cat authelia/config/notification.txt
   ```
3. Buka link tersebut di HP, scan QR Code dengan **Google Authenticator**.
4. Buka `https://nalar.bangkit.io` — selesai!
