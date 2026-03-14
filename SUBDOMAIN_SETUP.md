# Subdomain Setup: remove.khanjansevakendra.shop

Aapka existing website: `https://khanjansevakendra.shop`  
Naya background removal service: `https://remove.khanjansevakendra.shop`

---

## Step 1: GitHub Pe Push Karo

```bash
cd /Users/arbaz/Downloads/rembg-main

# Push karo
./github_push.sh

# Ya manual:
git add .
git commit -m "Deploy remove.khanjansevakendra.shop subdomain"
git push origin main
```

---

## Step 2: Railway Pe Deploy Karo

### 2.1 New Project Create Karo

**Important:** Is baar alag project name use karo:

1. https://railway.app/ pe jao
2. **New Project** → **Deploy from GitHub**
3. Repository select karo
4. Project name: `khanjanseva-remove` (ya kuch bhi alag)

### 2.2 Environment Variables

```
GOOGLE_CLIENT_SECRET = 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
SESSION_SECRET_KEY = (openssl rand -hex 32)
INSTAMOJO_API_KEY = 01c6b914d4f8e224cb4b6bdceaeb5b77
INSTAMOJO_AUTH_TOKEN = d8ea03ef36c426ab2c10891cabd03d8c
INSTAMOJO_SALT = 4e57693050da4345984d7d1360149032
```

### 2.3 Domain Add Karo

Railway Dashboard → Settings → Domains:

1. **Custom Domain** pe click karo
2. Enter: `remove.khanjansevakendra.shop`
3. **Add Domain**

Railway CNAME value dega, copy karo.

---

## Step 3: GoDaddy DNS Configuration

Apne GoDaddy account pe jao:

### DNS Management:

**Add New Record:**

| Type | Name | Value | TTL |
|------|------|-------|-----|
| CNAME | remove | `your-railway-app.up.railway.app` | 600 |

**Example:**
```
Type: CNAME
Name: remove
Value: khanjanseva-remove.up.railway.app
TTL: 600 seconds
```

**Save**

---

## Step 4: Google OAuth Update

### Google Cloud Console:
https://console.cloud.google.com/apis/credentials

**OAuth 2.0 Client ID** → Edit

### Authorized Redirect URIs:
```
https://remove.khanjansevakendra.shop/auth/callback
```

### Authorized JavaScript Origins:
```
https://remove.khanjansevakendra.shop
```

**Save Changes**

---

## Step 5: Instamojo Webhook Update

### Instamojo Dashboard:
https://www.instamojo.com/

**API & Plugins** → **Webhooks** → **New Webhook**

```
Webhook URL: https://remove.khanjansevakendra.shop/api/payments/webhook
Secret: 4e57693050da4345984d7d1360149032
```

---

## Step 6: Update Main Website

Apne main website `khanjansevakendra.shop` pe link add karo:

**HTML Code:**
```html
<a href="https://remove.khanjansevakendra.shop" class="btn">
  🖼️ Remove Background
</a>
```

---

## Final URLs

| Service | URL |
|---------|-----|
| Main Website | https://khanjansevakendra.shop |
| Background Removal | https://remove.khanjansevakendra.shop |
| Login | https://remove.khanjansevakendra.shop/login |
| Dashboard | https://remove.khanjansevakendra.shop/dashboard |
| Admin Panel | https://remove.khanjansevakendra.shop/admin |

---

## DNS Summary

### GoDaddy DNS Records:

**Existing (aapka current website):**
```
Type: A
Name: @
Value: (aapka server IP)
```

**New (subdomain for remove bg):**
```
Type: CNAME
Name: remove
Value: your-railway-app.up.railway.app
```

---

## Troubleshooting

### Subdomain Not Loading

1. Check DNS:
```bash
dig remove.khanjansevakendra.shop
```

2. Railway mein domain status check karo

### SSL Certificate Error

Railway automatically SSL certificate generate karega subdomain ke liye bhi. Wait 24 hours.

### Google Login Not Working

Redirect URI exact hona chahiye:
- ✅ `https://remove.khanjansevakendra.shop/auth/callback`
- ❌ `https://khanjansevakendra.shop/auth/callback` (galat)

---

## Commands

```bash
# Check subdomain DNS
dig remove.khanjansevakendra.shop

# Test website
curl -I https://remove.khanjansevakendra.shop

# Check SSL
openssl s_client -connect remove.khanjansevakendra.shop:443
```

---

## Summary

| Setting | Value |
|---------|-------|
| **Subdomain** | remove.khanjansevakendra.shop |
| **Platform** | Railway (New Project) |
| **DNS Type** | CNAME |
| **DNS Name** | remove |
| **Google OAuth** | https://remove.khanjansevakendra.shop/auth/callback |
| **Payment Webhook** | https://remove.khanjansevakendra.shop/api/payments/webhook |

---

Ready! 🚀
