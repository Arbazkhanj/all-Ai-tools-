# 🚀 Khan Jan Seva Kendra - Deployment Guide

## Quick Start (5 Minutes)

### 1️⃣ GitHub Pe Upload Karo

```bash
# 1. GitHub par new repository banao (khan-jan-seva-kendra)

# 2. Local project mein commands run karo
cd /Users/arbaz/Downloads/rembg-main

git init
git add .
git commit -m "Initial commit"

git remote add origin https://github.com/YOUR_USERNAME/khan-jan-seva-kendra.git
git branch -M main
git push -u origin main
```

### 2️⃣ Railway Pe Deploy Karo (Recommended)

```bash
# Railway CLI install karo
npm install -g @railway/cli

# Login karo
railway login

# Deploy karo
cd /Users/arbaz/Downloads/rembg-main
railway init
railway up
```

✅ **Done!** Railway automatically URL de dega.

---

## 📋 Complete Setup

### Option A: Railway (Easiest) 🚀

**Step 1:** Railway CLI install
```bash
npm install -g @railway/cli
```

**Step 2:** Login & Deploy
```bash
cd /Users/arbaz/Downloads/rembg-main
railway login
railway init
railway up
```

**Step 3:** Environment Variables set karo
```bash
railway variables set GOOGLE_CLIENT_ID=your-client-id
railway variables set GOOGLE_CLIENT_SECRET=your-secret
```

**Step 4:** Domain check karo
```bash
railway domain
```

### Option B: Render

**Step 1:** [render.com](https://render.com) pe jao

**Step 2:** New Web Service → Connect GitHub

**Step 3:** Settings:
- **Name**: `khan-jan-seva`
- **Runtime**: Python
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `rembg s --host 0.0.0.0 --port $PORT`

**Step 4:** Deploy!

### Option C: Docker

```bash
# Build
docker build -t khan-jan-seva .

# Run
docker run -p 7860:7860 \
  -e GOOGLE_CLIENT_ID=xxx \
  -e GOOGLE_CLIENT_SECRET=xxx \
  khan-jan-seva
```

---

## 🔧 Google OAuth Setup (Production)

**Important:** Production ke liye Google Cloud Console mein settings update karo:

```
Authorized JavaScript Origins:
- https://your-app.railway.app
- https://your-app.onrender.com

Authorized Redirect URIs:
- https://your-app.railway.app/auth/callback
- https://your-app.onrender.com/auth/callback
```

---

## 📦 Files Included

| File | Purpose |
|------|---------|
| `Dockerfile` | Docker image build |
| `railway.json` | Railway config |
| `render.yaml` | Render config |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Git ignore rules |
| `deploy.sh` | Deployment script |

---

## 🌐 Live URL Examples

- Railway: `https://khan-jan-seva.up.railway.app`
- Render: `https://khan-jan-seva.onrender.com`

---

## ⚡ Models Download

**Note:** Models (2GB+) automatically download on first use. First request thoda slow hoga, uske baad fast!

---

## 🆘 Troubleshooting

### Issue: Models not downloading
**Solution:** First request mein 2-3 min lag sakte hain. Wait karo.

### Issue: Google Login not working
**Solution:** Google Cloud Console mein authorized URLs update karo.

### Issue: Build fails
**Solution:** `requirements.txt` check karo, all dependencies listed hain.

---

## 🎉 Ready!

Aapka app live hai! 🚀

URL: `https://your-app.up.railway.app` (ya jo bhi platform use kiya)

Koi bhi issue ho toh batana! 👍
