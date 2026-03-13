# GitHub Upload & Live Deployment Guide
## Khan Jan Seva Kendra - Background Remover

---

## 📁 Step 1: GitHub Pe Upload Karna

### 1.1 Git Repository Initialize Karo

```bash
# Project folder mein jao
cd /Users/arbaz/Downloads/rembg-main

# Git initialize karo
git init

# Sab files add karo (models chhod ke)
git add .

# Commit karo
git commit -m "Initial commit - Khan Jan Seva Kendra"
```

### 1.2 GitHub Repository Banao

1. [github.com](https://github.com) pe jao
2. **New Repository** click karo
3. Name: `khan-jan-seva-kendra`
4. **Create Repository**
5. Commands copy karo

### 1.3 Push Karo GitHub Pe

```bash
# GitHub repository connect karo
git remote add origin https://github.com/YOUR_USERNAME/khan-jan-seva-kendra.git

# Push karo
git branch -M main
git push -u origin main
```

---

## ⚠️ Important: Models Ke Liye (2GB+ Files)

GitHub pe 100MB se bade files allowed nahi hain. Models alag se handle karo:

### Option A: Git LFS (Large File Storage)

```bash
# Git LFS install karo
git lfs install

# Track large files
git lfs track "*.onnx"

# Add .gitattributes
git add .gitattributes
git commit -m "Track ONNX models with LFS"

# Models add karo (time lagega)
git add ~/.u2net/*.onnx
git commit -m "Add all AI models"
git push
```

### Option B: Models Ko Ignore Karo (Recommended)

`.gitignore` file mein add karo:

```gitignore
# Models - Ye download ho jayenge
*.onnx
models/
~/.u2net/

# Python
__pycache__/
*.py[cod]
*$py.class
.env
.venv
venv/

# IDE
.vscode/
.idea/
```

Phir deployment ke waqt models auto-download ho jayenge.

---

## 🌐 Step 2: Live Deploy Karna

### Option 1: Railway (Recommended - Free & Easy)

#### 2.1.1 Railway Account Banao
1. [railway.app](https://railway.app) pe jao
2. GitHub se login karo

#### 2.1.2 Deploy Karo

```bash
# Railway CLI install
npm install -g @railway/cli

# Login
railway login

# Project link karo
railway link

# Deploy
railway up
```

Ya web se:
1. **New Project** → **Deploy from GitHub repo**
2. Apna repo select karo
3. **Deploy** click karo

#### 2.1.3 Environment Variables Set Karo

Railway dashboard mein:
```
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
```

---

### Option 2: Render (Free)

#### 2.2.1 [render.com](https://render.com) Pe Jao

1. **New Web Service** click karo
2. GitHub repo connect karo
3. Settings:
   - **Name**: khan-jan-seva
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `rembg s --host 0.0.0.0 --port $PORT`

#### 2.2.2 Create `requirements.txt`

```txt
# requirements.txt
rembg[cpu,cli]
python-jose
authlib
itsdangerous
google-auth
```

#### 2.2.3 Create `render.yaml`

```yaml
services:
  - type: web
    name: khan-jan-seva
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: rembg s --host 0.0.0.0 --port $PORT
    envVars:
      - key: GOOGLE_CLIENT_ID
        sync: false
      - key: GOOGLE_CLIENT_SECRET
        sync: false
```

---

### Option 3: Heroku

```bash
# Heroku CLI install karo (agar nahi hai)

# Login
heroku login

# App create karo
heroku create khan-jan-seva-kendra

# Git push se deploy
heroku git:remote -a khan-jan-seva-kendra
git push heroku main

# Logs check karo
heroku logs --tail
```

**Create `Procfile`:**
```
web: rembg s --host 0.0.0.0 --port $PORT
```

**Create `runtime.txt`:**
```
python-3.11.0
```

---

### Option 4: Docker (Best for Models)

#### 2.4.1 Create `Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Create models directory
RUN mkdir -p /root/.u2net

# Download script
COPY download_models.py .
RUN python download_models.py

# Expose port
EXPOSE 7860

# Run
CMD ["rembg", "s", "--host", "0.0.0.0", "--port", "7860"]
```

#### 2.4.2 Create `docker-compose.yml`

```yaml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "7860:7860"
    volumes:
      - models:/root/.u2net
    environment:
      - GOOGLE_CLIENT_ID=${GOOGLE_CLIENT_ID}
      - GOOGLE_CLIENT_SECRET=${GOOGLE_CLIENT_SECRET}

volumes:
  models:
```

#### 2.4.3 Build & Run

```bash
# Build
docker-compose up --build

# Ya
docker build -t khan-jan-seva .
docker run -p 7860:7860 -v $(pwd)/models:/root/.u2net khan-jan-seva
```

---

## 📦 Step 3: Auto-Download Models Script

**Create `download_models.py`:**

```python
#!/usr/bin/env python3
"""Download all models on deployment"""

import os
import sys

MODELS = [
    ("u2net", "u2net.onnx"),
    ("u2netp", "u2netp.onnx"),
    ("u2net_human_seg", "u2net_human_seg.onnx"),
    ("u2net_cloth_seg", "u2net_cloth_seg.onnx"),
    ("silueta", "silueta.onnx"),
    ("isnet-general-use", "isnet-general-use.onnx"),
    ("isnet-anime", "isnet-anime.onnx"),
    ("bria-rmbg", "bria-rmbg-2.0.onnx"),
    ("sam", "sam"),  # Special case
]

print("📥 Downloading models...")

for model_name, filename in MODELS:
    try:
        print(f"  Downloading {model_name}...", end=" ")
        from rembg.session_factory import new_session
        session = new_session(model_name)
        print("✅")
    except Exception as e:
        print(f"❌ {e}")

print("✨ All models ready!")
```

---

## 🚀 Quick Deploy Checklist

### 1. Files Check Karo:
```bash
ls -la
# Hona chahiye:
# - Dockerfile (agar Docker use kar rahe ho)
# - requirements.txt
# - Procfile (Heroku ke liye)
# - render.yaml (Render ke liye)
# - .gitignore
```

### 2. Environment Variables Set Karo:
```bash
# Production ke liye Google OAuth credentials
GOOGLE_CLIENT_ID=your-production-client-id
GOOGLE_CLIENT_SECRET=your-production-secret
```

### 3. Google OAuth Settings Update Karo:
Google Cloud Console mein:
```
Authorized JavaScript Origins:
- https://your-app.com
- https://your-app.railway.app

Authorized Redirect URIs:
- https://your-app.com/auth/callback
- https://your-app.railway.app/auth/callback
```

---

## 🎯 Recommended: Railway (Easiest)

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login
railway login

# 3. Initialize
railway init

# 4. Deploy
railway up

# 5. Domain milegi automatically
# Example: https://khan-jan-seva.up.railway.app
```

---

## 📊 Deployment Comparison

| Platform | Free Tier | Models | Difficulty | Best For |
|----------|-----------|--------|------------|----------|
| **Railway** | ✅ $5/month credit | Auto-download | Easy | Production |
| **Render** | ✅ | Auto-download | Easy | Production |
| **Heroku** | ✅ (sleep after 30min) | Auto-download | Medium | Testing |
| **Docker** | Self-hosted | Persistent | Hard | Advanced |

---

## ⚡ Quick Commands

```bash
# GitHub push
git add .
git commit -m "Ready for deployment"
git push origin main

# Railway deploy
railway up

# Render (automatic on push)
# Just push to GitHub

# Docker
docker-compose up -d
```

---

## 🔥 Live URL Milne Ke Baad

1. **Test karo**: `https://your-app.com`
2. **Login check karo**: `https://your-app.com/login`
3. **API test karo**: `https://your-app.com/api`
4. **Models download honge automatically** (first time thoda slow)

**Koi bhi issue aaye toh batana!** 🚀
