# Custom Domain Deployment Guide

Agar apke paas domain hai (e.g., `khanjanseva.com`), toh ye steps follow karo.

---

## Option 1: Railway + Custom Domain (Recommended)

### Step 1: Railway Pe Deploy Karo

1. https://railway.app/ pe jao
2. GitHub repo connect karo
3. Deploy ho jayega (default URL milegi)

### Step 2: Custom Domain Add Karo

1. Railway Dashboard → Project → Settings → Domains
2. **Generate Domain** → Copy the default URL
3. **Custom Domain** pe click karo
4. Apna domain daldo: `khanjanseva.com` (ya jo bhi hai)

### Step 3: DNS Records Configure Karo

Apne domain provider (GoDaddy/Namecheap/Cloudflare) pe jao:

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | @ | `your-app.up.railway.app` | 600 |
| CNAME | www | `your-app.up.railway.app` | 600 |

**Example:**
```
Type: CNAME
Name: @ (ya khanjanseva.com)
Value: khanjanseva-production.up.railway.app
```

### Step 4: SSL Certificate (Auto)

Railway automatically SSL certificate provide karta hai:
- ✅ HTTPS enabled
- ✅ Auto-renewal
- ✅ No manual setup

**Wait Time:** DNS propagate hone mein 5-30 minutes lag sakte hain.

---

## Option 2: Render + Custom Domain

### Step 1: Deploy on Render

1. https://render.com/ pe jao
2. GitHub repo connect karo
3. Deploy

### Step 2: Custom Domain Add Karo

1. Render Dashboard → Project → Settings → Custom Domains
2. **Add Domain**
3. Domain name: `khanjanseva.com`

### Step 3: DNS Records

Render apko specific DNS values dega:

```
Type: CNAME
Name: khanjanseva.com
Value: khanjanseva.onrender.com (ya jo render dega)
```

Ya phir:
```
Type: A Record
Name: @
Value: 216.24.57.1 (Render ka IP - dashboard pe milega)
```

### Step 4: SSL (Auto)

Render automatically Let's Encrypt SSL certificate generate karega.

---

## Option 3: VPS/Dedicated Server + Domain

Agar apne paas VPS hai (DigitalOcean, AWS, Linode), toh ye setup karo:

### Step 1: Server Setup

```bash
# Domain point karo server IP pe
# A Record: khanjanseva.com → Your.Server.IP.Address
```

### Step 2: Install Dependencies

```bash
ssh root@your-server-ip

apt update
apt install -y python3 python3-pip python3-venv nginx certbot python3-certbot-nginx git
```

### Step 3: Code Clone Karo

```bash
cd /opt
git clone https://github.com/yourusername/khanjanseva.git
cd khanjanseva
```

### Step 4: Environment Variables

```bash
nano /opt/khanjanseva/.env
```

```env
GOOGLE_CLIENT_SECRET=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
SESSION_SECRET_KEY=your-random-secret-key
DATABASE_URL=sqlite:///./data/rembg_payments.db
INSTAMOJO_API_KEY=01c6b914d4f8e224cb4b6bdceaeb5b77
INSTAMOJO_AUTH_TOKEN=d8ea03ef36c426ab2c10891cabd03d8c
INSTAMOJO_SALT=4e57693050da4345984d7d1360149032
```

### Step 5: Application Setup

```bash
# Virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Data directory
mkdir -p data
```

### Step 6: Systemd Service

```bash
nano /etc/systemd/system/khanjanseva.service
```

```ini
[Unit]
Description=Khan Jan Seva Kendra
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/khanjanseva
EnvironmentFile=/opt/khanjanseva/.env
ExecStart=/opt/khanjanseva/venv/bin/python -m rembg s --host 127.0.0.1 --port 8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
systemctl daemon-reload
systemctl enable khanjanseva
systemctl start khanjanseva
```

### Step 7: Nginx Configuration

```bash
nano /etc/nginx/sites-available/khanjanseva
```

```nginx
server {
    listen 80;
    server_name khanjanseva.com www.khanjanseva.com;

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

    client_max_body_size 50M;
}
```

```bash
ln -s /etc/nginx/sites-available/khanjanseva /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 8: SSL Certificate (Let's Encrypt)

```bash
certbot --nginx -d khanjanseva.com -d www.khanjanseva.com

# Auto-renewal test
certbot renew --dry-run
```

---

## Step 4: Environment Variables Update (Important!)

Deployment platform pe ye variables update karo:

### Railway/Render Dashboard → Variables:

```env
# Update these with your domain
BASE_URL=https://khanjanseva.com
FRONTEND_URL=https://khanjanseva.com
```

---

## Step 5: Google OAuth Update (Critical!)

### Google Cloud Console:

1. https://console.cloud.google.com/apis/credentials
2. OAuth 2.0 Client ID → Edit

### Authorized Redirect URIs:
```
https://khanjanseva.com/auth/callback
https://www.khanjanseva.com/auth/callback
```

### Authorized JavaScript Origins:
```
https://khanjanseva.com
https://www.khanjanseva.com
```

**Save Changes**

---

## Step 6: Instamojo Webhook Update

### Instamojo Dashboard → API & Plugins → Webhooks:

| Setting | Value |
|---------|-------|
| Webhook URL | `https://khanjanseva.com/api/payments/webhook` |
| Secret | `4e57693050da4345984d7d1360149032` |

**Save**

---

## DNS Configuration Summary

### Cloudflare (Recommended - Free SSL + CDN)

```
Type: CNAME
Name: @
Target: your-app.up.railway.app
Proxy Status: DNS only (ya Proxied for CDN)
```

### GoDaddy:

```
Type: CNAME
Host: @
Points to: your-app.up.railway.app
TTL: 600 seconds
```

### Namecheap:

```
Type: CNAME Record
Host: @
Value: your-app.up.railway.app
TTL: Automatic
```

---

## Verification Checklist

Domain setup complete hone ke baad verify karo:

- [ ] Domain load ho raha hai: `https://khanjanseva.com`
- [ ] SSL certificate valid hai (Green lock in browser)
- [ ] Google login kaam kar raha hai
- [ ] Dashboard accessible hai
- [ ] Payments working hain
- [ ] Webhook receiving ho raha hai

---

## Troubleshooting

### DNS Not Propagating

```bash
# Check DNS status
dig khanjanseva.com
dig www.khanjanseva.com

# Ya online: https://dnschecker.org/
```

Wait 24-48 hours for full propagation.

### SSL Certificate Error

Railway/Render automatically handle karte hain. Agar manual VPS pe ho:

```bash
# Certificate renewal force karo
certbot renew --force-renewal
systemctl restart nginx
```

### "Your connection is not private"

1. SSL certificate expire ho gaya hai
2. Domain mismatch hai
3. Time sync issue hai server pe

```bash
# Time sync
 timedatectl set-ntp true
```

---

## Domain + Hosting Cost Estimate

| Component | Provider | Cost (Monthly) |
|-----------|----------|---------------|
| Domain | Namecheap/GoDaddy | ₹500-800/year |
| Hosting | Railway | Free - $5/month |
| Hosting | Render | Free - $7/month |
| Hosting | VPS (DigitalOcean) | $5-10/month |
| CDN | Cloudflare | Free |
| SSL | Let's Encrypt | Free |

**Total:** ₹500-1500/month depending on traffic

---

## Commands Quick Reference

```bash
# Check if domain is pointing correctly
curl -I https://khanjanseva.com

# Check SSL certificate
openssl s_client -connect khanjanseva.com:443

# DNS lookup
nslookup khanjanseva.com

# Test webhook
curl -X POST https://khanjanseva.com/api/payments/webhook \
  -d "test=data"
```

---

Apna domain name batao, mai exact DNS records bata dunga! 🚀
