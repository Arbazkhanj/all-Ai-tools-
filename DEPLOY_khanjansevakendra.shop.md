# Deploy khanjansevakendra.shop - Complete Guide

Domain: **khanjansevakendra.shop**  
Target: Production deployment with custom domain

---

## Step 1: GitHub Pe Push Karo

```bash
cd /Users/arbaz/Downloads/rembg-main

# GitHub push
./github_push.sh

# Ya manual:
git add .
git commit -m "Production deployment for khanjansevakendra.shop"
git push origin main
```

---

## Step 2: Railway Pe Deploy Karo (Recommended)

### 2.1 Railway Account Setup
1. https://railway.app/ pe jao
2. GitHub se login karo
3. **New Project** → **Deploy from GitHub repo**
4. `khanjanseva` repository select karo

### 2.2 Environment Variables Add Karo

Railway Dashboard → Variables:

```
GOOGLE_CLIENT_SECRET = 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
SESSION_SECRET_KEY = (generate random string - 32 characters)
INSTAMOJO_API_KEY = 01c6b914d4f8e224cb4b6bdceaeb5b77
INSTAMOJO_AUTH_TOKEN = d8ea03ef36c426ab2c10891cabd03d8c
INSTAMOJO_SALT = 4e57693050da4345984d7d1360149032
```

**Secret Key Generate Karo:**
```bash
openssl rand -hex 32
```

### 2.3 Domain Connect Karo

Railway Dashboard → Settings → Domains:
1. **Custom Domain** pe click karo
2. Enter: `khanjansevakendra.shop`
3. **Add Domain**

Railway apko DNS records dega kuch aise:
```
CNAME: khanjansevakendra.shop → your-app.up.railway.app
```

---

## Step 3: DNS Configuration (Very Important!)

Apne domain provider pe jao (jahan se `khanjansevakendra.shop` liya hai):

### DNS Records Add Karo:

| Type | Host/Name | Value/Points to | TTL |
|------|-----------|-----------------|-----|
| CNAME | @ | `your-railway-app.up.railway.app` | 600 |
| CNAME | www | `your-railway-app.up.railway.app` | 600 |

**Note:** Railway dashboard pe exact CNAME value milega. Wahi use karna hai.

### Common Domain Providers:

**GoDaddy:**
1. DNS Management → Add Record
2. Type: CNAME
3. Name: @
4. Value: Railway ka URL

**Namecheap:**
1. Domain List → Manage
2. Advanced DNS → Add New Record
3. Type: CNAME Record
4. Host: @
5. Value: Railway ka URL

**Cloudflare (Recommended for free SSL + CDN):**
1. DNS → Add Record
2. Type: CNAME
3. Name: @
4. Target: Railway ka URL
5. Proxy Status: DNS only (pehle), baad mein Proxied kar sakte ho

---

## Step 4: Google OAuth Update (CRITICAL!)

### Google Cloud Console:
https://console.cloud.google.com/apis/credentials

**OAuth 2.0 Client ID** → Edit

### Authorized Redirect URIs Add Karo:
```
https://khanjansevakendra.shop/auth/callback
https://www.khanjansevakendra.shop/auth/callback
```

### Authorized JavaScript Origins Add Karo:
```
https://khanjansevakendra.shop
https://www.khanjansevakendra.shop
```

**Save Changes**

---

## Step 5: Instamojo Webhook Update

### Instamojo Dashboard:
https://www.instamojo.com/

**API & Plugins** → **Webhooks** → **New Webhook**

| Setting | Value |
|---------|-------|
| Webhook URL | `https://khanjansevakendra.shop/api/payments/webhook` |
| Secret/Salt | `4e57693050da4345984d7d1360149032` |

**Save**

---

## Step 6: Wait for DNS Propagation

DNS propagate hone mein time lagta hai:
- **Usually:** 5-30 minutes
- **Maximum:** 24-48 hours

Check karo:
```bash
dig khanjansevakendra.com
nslookup khanjansevakendra.com
```

Ya online: https://dnschecker.org/

---

## Step 7: Verify Deployment

### Checklist:

- [ ] **Website Load:** https://khanjansevakendra.shop
- [ ] **SSL Certificate:** Green lock in browser
- [ ] **Google Login:** Working
- [ ] **Dashboard:** https://khanjansevakendra.shop/dashboard
- [ ] **Image Processing:** Working
- [ ] **Payments:** Test payment try karo

---

## Final URLs

| Page | URL |
|------|-----|
| Home | https://khanjansevakendra.shop |
| Login | https://khanjansevakendra.shop/login |
| Dashboard | https://khanjansevakendra.shop/dashboard |
| Admin | https://khanjansevakendra.shop/admin |
| API Docs | https://khanjansevakendra.shop/api |

---

## Troubleshooting

### Domain Not Loading

1. DNS records check karo:
```bash
dig CNAME khanjansevakendra.shop
```

2. Railway mein domain status check karo:
   - Dashboard → Settings → Domains
   - Verify ho raha hai ya nahi

### SSL Certificate Error

Railway automatically SSL provide karta hai. Agar error aata hai:
1. Wait 24 hours
2. Domain remove karke dobara add karo
3. Railway support contact karo

### Google Login Not Working

Google Console mein check karo:
- Redirect URI exact match hona chahiye
- No trailing slash `/`
- `https` hona chahiye, `http` nahi

---

## Commands Quick Reference

```bash
# Check domain DNS
dig khanjansevakendra.shop

# Check SSL certificate
openssl s_client -connect khanjansevakendra.shop:443

# Test website
curl -I https://khanjansevakendra.shop

# Test webhook
curl -X POST https://khanjansevakendra.shop/api/payments/webhook \
  -d "test=data"
```

---

## Summary Timeline

| Step | Time |
|------|------|
| GitHub Push | 2 minutes |
| Railway Deploy | 5 minutes |
| DNS Setup | 5 minutes |
| DNS Propagation | 5-30 minutes |
| Google OAuth Update | 2 minutes |
| Instamojo Webhook | 2 minutes |
| **Total** | **20-50 minutes** |

---

Ready to deploy! 🚀
