# NALAR AI Coding Harness (Docker + Coolify Traefik + Authelia 2FA)
*Personal AI coding agent harness dengan branding **NALAR** dan proteksi **Google Authenticator (TOTP)**.*

Stack:
- **`nalar-engine`**: Custom-branded `pingdotgg/t3code` (prebuilt release + branding NALAR + PWA manifest + pre-installed `claude` & `codex` CLIs).
- **`nalar-authelia`**: Authelia v4.38 2FA portal (`auth.bangkit.io`) menggunakan Google Authenticator.
- **Coolify Traefik (`coolify-proxy`)**: Reverse proxy & SSL Let's Encrypt otomatis via `/data/coolify/proxy/dynamic/nalar.yaml` (tanpa bentrok port 80/443).

---

## Cara Deploy / Update di VPS

```bash
cd /root/nalar-stack
git pull
chmod +x deploy.sh
./deploy.sh
```

## Perintah Penting di VPS

- **Cek link aktivasi QR Google Authenticator:**
  ```bash
  cat /root/nalar-stack/authelia/config/notification.txt
  ```
- **Ganti password user `admin`:**
  ```bash
  docker run --rm -it authelia/authelia:4.38 authelia crypto hash generate argon2
  # Paste hasil Digest ke /root/nalar-stack/authelia/config/users_database.yml
  docker restart nalar-authelia
  ```
- **Pairing HP ke NALAR (jika diminta pairing code):**
  ```bash
  docker exec -it nalar-engine nalar pair --base-dir /data/t3
  ```
- **Login AI Provider CLI di dalam container NALAR:**
  ```bash
  # Claude Code:
  docker exec -it nalar-engine claude auth login
  # OpenAI Codex:
  docker exec -it nalar-engine codex login
  ```
