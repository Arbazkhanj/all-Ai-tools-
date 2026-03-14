# Production Deployment Guide

Is guide mein GitHub se production server pe deploy karne ka process hai.

## Option 1: Heroku Deployment (Easiest)

### Step 1: Heroku Setup

1. **Heroku Account** banao: https://signup.heroku.com/

2. **Heroku CLI Install** karo:
```bash
# MacOS
brew install heroku/brew/heroku

# Login
heroku login
```

### Step 2: App Create Karo

```bash
# Heroku app create karo
heroku create khanjanseva-backend

# Ya apna custom name
heroku create your-app-name
```

### Step 3: Environment Variables Set Karo

```bash
# Required environment variables
heroku config:set GOOGLE_CLIENT_SECRET='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'
heroku config:set SESSION_SECRET_KEY='your-random-secret-key-here'
heroku config:set INSTAMOJO_API_KEY='01c6b914d4f8e224cb4b6bdceaeb5b77'
heroku config:set INSTAMOJO_AUTH_TOKEN='d8ea03ef36c426ab2c10891cabd03d8c'
heroku config:set INSTAMOJO_SALT='4e57693050da4345984d7d1360149032'

# Database (PostgreSQL)
heroku addons:create heroku-postgresql:mini
```

### Step 4: Deploy Karo

```bash
# Code push karo
git push heroku main

# Logs check karo
heroku logs --tail
```

**Live URL:** `https://your-app-name.herokuapp.com`

---

## Option 2: Railway Deployment (Recommended)

### Step 1: Railway Setup

1. **Railway Account** banao: https://railway.app/
2. **GitHub** connect karo

### Step 2: Project Create Karo

1. Railway dashboard pe **New Project**
2. **Deploy from GitHub repo** select karo
3. Repository select karo

### Step 3: Environment Variables

Railway dashboard → Variables:

```env
GOOGLE_CLIENT_SECRET=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
SESSION_SECRET_KEY=your-random-secret-key
INSTAMOJO_API_KEY=01c6b914d4f8e224cb4b6bdceaeb5b77
INSTAMOJO_AUTH_TOKEN=d8ea03ef36c426ab2c10891cabd03d8c
INSTAMOJO_SALT=4e57693050da4345984d7d1360149032
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

### Step 4: Auto Deploy

GitHub pe push karte hi automatic deploy hoga!

---

## Option 3: VPS/Server Deployment (DigitalOcean/AWS/Linode)

### Step 1: Server Setup

```bash
# Ubuntu server pe SSH karo
ssh root@your-server-ip

# Dependencies install karo
apt update
apt install -y python3 python3-pip python3-venv nginx git

# Project directory
mkdir -p /opt/rembg
cd /opt/rembg
```

### Step 2: Code Clone Karo

```bash
# GitHub se clone karo
git clone https://github.com/yourusername/rembg-main.git .

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Dependencies install
pip install -r requirements.txt
```

### Step 3: Environment Variables

```bash
# .env file create karo
nano /opt/rembg/.env
```

```env
GOOGLE_CLIENT_SECRET=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
SESSION_SECRET_KEY=your-random-secret-key-here
DATABASE_URL=sqlite:///./rembg_payments.db
INSTAMOJO_API_KEY=01c6b914d4f8e224cb4b6bdceaeb5b77
INSTAMOJO_AUTH_TOKEN=d8ea03ef36c426ab2c10891cabd03d8c
INSTAMOJO_SALT=4e57693050da4345984d7d1360149032
```

### Step 4: Systemd Service

```bash
sudo nano /etc/systemd/system/rembg.service
```

```ini
[Unit]
Description=Khan Jan Seva Kendra Background Remover
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/rembg
Environment=GOOGLE_CLIENT_SECRET=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
Environment=SESSION_SECRET_KEY=your-random-secret-key
Environment=DATABASE_URL=sqlite:///./rembg_payments.db
Environment=INSTAMOJO_API_KEY=01c6b914d4f8e224cb4b6bdceaeb5b77
Environment=INSTAMOJO_AUTH_TOKEN=d8ea03ef36c426ab2c10891cabd03d8c
Environment=INSTAMOJO_SALT=4e57693050da4345984d7d1360149032
ExecStart=/opt/rembg/venv/bin/python -m rembg s --host 0.0.0.0 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
# Service enable karo
sudo systemctl daemon-reload
sudo systemctl enable rembg
sudo systemctl start rembg

# Status check karo
sudo systemctl status rembg
```

### Step 5: Nginx Reverse Proxy

```bash
sudo nano /etc/nginx/sites-available/rembg
```

```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Increase upload size for images
    client_max_body_size 50M;
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/rembg /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 6: SSL Certificate (HTTPS)

```bash
# Certbot install karo
sudo apt install certbot python3-certbot-nginx

# SSL certificate generate karo
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal check karo
sudo certbot renew --dry-run
```

---

## Option 4: Docker Deployment

### Dockerfile

Already created hai:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Environment variables
ENV GOOGLE_CLIENT_SECRET=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
ENV SESSION_SECRET_KEY=your-secret-key
ENV DATABASE_URL=sqlite:///./rembg_payments.db

# Expose port
EXPOSE 8000

# Run server
CMD ["python", "-m", "rembg", "s", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Commands

```bash
# Build image
docker build -t khanjanseva:latest .

# Run container
docker run -d \
  -p 8000:8000 \
  -e GOOGLE_CLIENT_SECRET='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' \
  -e SESSION_SECRET_KEY='your-secret' \
  -v $(pwd)/data:/app/data \
  --name khanjanseva \
  khanjanseva:latest

# View logs
docker logs -f khanjanseva
```

---

## GitHub Repository Setup

### Step 1: GitHub Pe Push Karo

```bash
# Initialize git (agar nahi hai)
git init

# All files add karo
git add .

# Commit karo
git commit -m "Initial production deployment"

# GitHub repo create karo (browser mein)
# https://github.com/new

# Remote add karo
git remote add origin https://github.com/yourusername/khanjanseva.git

# Push karo
git push -u origin main
```

### Step 2: GitHub Secrets Set Karo

Repository → Settings → Secrets and variables → Actions:

| Secret Name | Value |
|------------|-------|
| `GOOGLE_CLIENT_SECRET` | `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` |
| `SESSION_SECRET_KEY` | `your-random-secret-key` |
| `INSTAMOJO_API_KEY` | `01c6b914d4f8e224cb4b6bdceaeb5b77` |
| `INSTAMOJO_AUTH_TOKEN` | `d8ea03ef36c426ab2c10891cabd03d8c` |
| `INSTAMOJO_SALT` | `4e57693050da4345984d7d1360149032` |
| `DATABASE_URL` | `sqlite:///./rembg_payments.db` |

---

## Important: Production Checklist

### Security
- [ ] Strong `SESSION_SECRET_KEY` set karo (random 32+ characters)
- [ ] `GOOGLE_CLIENT_SECRET` secure rakho
- [ ] Database backups configure karo
- [ ] HTTPS enable karo (SSL certificate)

### Instamojo Configuration
- [ ] Webhook URL update karo: `https://yourdomain.com/api/payments/webhook`
- [ ] Production API keys use karo (test se alag)
- [ ] KYC complete karo

### Google OAuth
- [ ] Authorized redirect URIs update karo:
  - `https://yourdomain.com/auth/callback`
- [ ] Authorized JavaScript origins add karo:
  - `https://yourdomain.com`

### Monitoring
- [ ] Logs setup karo
- [ ] Uptime monitoring (UptimeRobot, etc.)
- [ ] Error tracking (Sentry, etc.)

---

## Environment Variables Summary

### Required Variables:

```bash
# Google OAuth
GOOGLE_CLIENT_SECRET=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

# Session Security
SESSION_SECRET_KEY=generate-random-32-char-string

# Database
DATABASE_URL=sqlite:///./rembg_payments.db
# Ya PostgreSQL: postgresql://user:pass@host/dbname

# Payments (Instamojo)
INSTAMOJO_API_KEY=01c6b914d4f8e224cb4b6bdceaeb5b77
INSTAMOJO_AUTH_TOKEN=d8ea03ef36c426ab2c10891cabd03d8c
INSTAMOJO_SALT=4e57693050da4345984d7d1360149032
```

### Generate Random Secret Key:

```bash
openssl rand -hex 32
```

Ya Python mein:
```python
import secrets
print(secrets.token_hex(32))
```

---

## Troubleshooting

### Server Start Nahi Ho Raha

```bash
# Logs check karo
journalctl -u rembg -f

# Ya
docker logs khanjanseva
```

### Database Errors

```bash
# Database permissions check karo
ls -la rembg_payments.db

# Database migrate karo (if needed)
python3 -c "from rembg.backend.database import init_db; init_db()"
```

### Payment Webhook Not Working

1. Webhook URL accessible hai?
```bash
curl -I https://yourdomain.com/api/payments/webhook
```

2. Instamojo dashboard mein webhook URL update karo

---

## Support

Deployment mein koi problem aaye toh:

1. Server logs check karo
2. GitHub issues create karo
3. Environment variables verify karo
