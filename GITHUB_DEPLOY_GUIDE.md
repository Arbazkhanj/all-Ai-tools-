# Complete GitHub & Deployment Guide

Ye guide GitHub pe push karne aur live deploy karne ke liye hai.

---

## Step 1: GitHub Repository Create Karo

### 1.1 GitHub Pe Jao
- https://github.com/new pe jao
- Repository name: `khanjanseva` (ya jo bhi naam pasand ho)
- Public ya Private select karo
- **Create repository** click karo

### 1.2 Repository URL Copy Karo
URL hoga kuch aisa:
```
https://github.com/yourusername/khanjanseva.git
```

---

## Step 2: Code Push Karo (2 Methods)

### Method A: Automated Script (Easy)

```bash
# Terminal mein project directory pe jao
cd /Users/arbaz/Downloads/rembg-main

# Push script run karo
./github_push.sh
```

Ye script automatically:
- Git init karega (agar nahi hai)
- Sab files add karega
- Commit karega
- Remote add karega
- GitHub pe push karega

### Method B: Manual Commands

```bash
# Project directory pe jao
cd /Users/arbaz/Downloads/rembg-main

# Git initialize (agar nahi hai)
git init

# All files add karo
git add .

# Commit karo
git commit -m "Initial production deployment"

# Remote add karo (apna username dalna)
git remote add origin https://github.com/yourusername/khanjanseva.git

# Push karo
git push -u origin main
```

---

## Step 3: Deployment Platform Choose Karo

### Option 1: Railway (Recommended - Free & Easy)

**Benefits:**
- Free tier available
- Auto-deploy on GitHub push
- PostgreSQL database included
- No credit card required

**Steps:**

1. **Railway Account** banao: https://railway.app/

2. **New Project** → **Deploy from GitHub repo**

3. **Repository select** karo (khanjanseva)

4. **Variables** add karo:
```
GOOGLE_CLIENT_SECRET = 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
SESSION_SECRET_KEY = (generate random string)
INSTAMOJO_API_KEY = 01c6b914d4f8e224cb4b6bdceaeb5b77
INSTAMOJO_AUTH_TOKEN = d8ea03ef36c426ab2c10891cabd03d8c
INSTAMOJO_SALT = 4e57693050da4345984d7d1360149032
```

5. **Deploy** ho jayega automatically!

**Live URL:** `https://khanjanseva-production.up.railway.app`

---

### Option 2: Render (Free)

**Benefits:**
- Completely free
- PostgreSQL database
- Custom domain support

**Steps:**

1. **Render Account** banao: https://render.com/

2. **New** → **Blueprint**

3. **Connect GitHub**

4. Repository select karo

5. **Environment Variables** add karo (same as Railway)

6. **Deploy**

**Live URL:** `https://khanjanseva.onrender.com`

---

### Option 3: Heroku (Paid)

**Note:** Heroku ka free tier band ho gaya hai, paid plan lena padega.

```bash
# Heroku CLI se
heroku create khanjanseva

# Environment variables
heroku config:set GOOGLE_CLIENT_SECRET='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'
heroku config:set SESSION_SECRET_KEY='your-secret'

# Deploy
git push heroku main
```

---

## Step 4: Environment Variables Setup

### Required Variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `GOOGLE_CLIENT_SECRET` | `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` | Google OAuth |
| `SESSION_SECRET_KEY` | Generate random 32+ chars | Session security |
| `INSTAMOJO_API_KEY` | `01c6b914d4f8e224cb4b6bdceaeb5b77` | Payment gateway |
| `INSTAMOJO_AUTH_TOKEN` | `d8ea03ef36c426ab2c10891cabd03d8c` | Payment auth |
| `INSTAMOJO_SALT` | `4e57693050da4345984d7d1360149032` | Webhook verification |

### Random Secret Key Generate Karo:

```bash
openssl rand -hex 32
```

Ya online: https://randomkeygen.com/

---

## Step 5: Google OAuth Configure Karo (Important!)

### Production Redirect URIs Update Karo:

1. **Google Cloud Console** → **APIs & Services** → **Credentials**

2. **OAuth 2.0 Client ID** pe click karo

3. **Authorized Redirect URIs** add karo:

**For Railway:**
```
https://khanjanseva-production.up.railway.app/auth/callback
```

**For Render:**
```
https://khanjanseva.onrender.com/auth/callback
```

**For Custom Domain:**
```
https://yourdomain.com/auth/callback
```

4. **Authorized JavaScript Origins** add karo:
```
https://khanjanseva-production.up.railway.app
https://khanjanseva.onrender.com
```

5. **Save** karo

---

## Step 6: Instamojo Webhook Configure Karo

### Instamojo Dashboard:

1. **API & Plugins** → **Webhooks**

2. **New Webhook** add karo:

| Field | Value |
|-------|-------|
| Webhook URL | `https://khanjanseva-production.up.railway.app/api/payments/webhook` |
| Secret | `4e57693050da4345984d7d1360149032` |

3. **Save** karo

---

## Step 7: Domain Connect Karo (Optional)

### Custom Domain Add Karo:

**Railway:**
1. Dashboard → Settings → Domains
2. **Add Custom Domain**
3. DNS records add karo

**Render:**
1. Dashboard → Settings → Custom Domains
2. **Add Domain**
3. DNS configure karo

### DNS Records:

| Type | Name | Value |
|------|------|-------|
| CNAME | @ | `khanjanseva-production.up.railway.app` |
| CNAME | www | `khanjanseva-production.up.railway.app` |

---

## Step 8: SSL/HTTPS (Auto)

Railway aur Render automatically SSL certificate provide karte hain:
- ✅ HTTPS enabled by default
- ✅ Auto-renewal

---

## Verification Checklist

Deployment ke baad verify karo:

- [ ] Website load ho raha hai: `https://your-domain.com`
- [ ] Login kaam kar raha hai (Google OAuth)
- [ ] Dashboard accessible hai
- [ ] Image processing kaam kar raha hai
- [ ] Payment integration working hai
- [ ] Webhook credits add kar raha hai

---

## Troubleshooting

### Error: "redirect_uri_mismatch"
**Solution:** Google Console mein redirect URI exactly match hona chahiye production URL se.

### Error: "Payment webhook not working"
**Solution:** Instamojo dashboard mein webhook URL https se start honi chahiye, http nahi.

### Error: "Database connection failed"
**Solution:** Railway/Render automatically database provide karte hain. Local SQLite use mat karo production mein.

### Error: "Session not persisting"
**Solution:** `SESSION_SECRET_KEY` set karo aur strong banao (32+ characters).

---

## Files Created for Deployment

| File | Purpose |
|------|---------|
| `Procfile` | Heroku config |
| `render.yaml` | Render config |
| `railway.json` | Railway config |
| `docker-compose.yml` | Docker deployment |
| `runtime.txt` | Python version |
| `.gitignore` | Git ignore rules |
| `.github/workflows/deploy.yml` | CI/CD pipeline |

---

## Quick Commands Summary

```bash
# GitHub push
./github_push.sh

# Heroku deploy
heroku create khanjanseva && git push heroku main

# Docker deploy
docker-compose up -d

# Local test
GOOGLE_CLIENT_SECRET='GOCSPX-...' rembg s --host 0.0.0.0 --port 7000
```

---

## Support

Deployment mein koi problem aaye toh:
1. Platform logs check karo (Railway/Render dashboard)
2. Environment variables verify karo
3. Google OAuth settings check karo

**Documentation:**
- `DEPLOYMENT.md` - Detailed deployment guide
- `WEBHOOK_SETUP.md` - Webhook configuration
- `GOOGLE_OAUTH_SETUP.md` - OAuth setup

---

**Ready to deploy! 🚀**
