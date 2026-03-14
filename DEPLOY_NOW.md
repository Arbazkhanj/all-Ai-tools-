# 🚀 Deploy khanjansevakendra.shop RIGHT NOW

**Domain:** khanjansevakendra.shop  
**Status:** Ready for deployment

---

## ⚡ Quick Deploy (15 Minutes)

### Step 1: Push Code to GitHub (2 min)

```bash
cd /Users/arbaz/Downloads/rembg-main
./github_push.sh
```

Ya manual:
```bash
git add .
git commit -m "Deploy khanjansevakendra.shop"
git push origin main
```

---

### Step 2: Deploy on Railway (5 min)

1. Go to https://railway.app/
2. Login with GitHub
3. Click **New Project** → **Deploy from GitHub**
4. Select your repository
5. Railway will automatically deploy

**Add Environment Variables:**
```
GOOGLE_CLIENT_SECRET = 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
SESSION_SECRET_KEY = (run: openssl rand -hex 32)
INSTAMOJO_API_KEY = 01c6b914d4f8e224cb4b6bdceaeb5b77
INSTAMOJO_AUTH_TOKEN = d8ea03ef36c426ab2c10891cabd03d8c
INSTAMOJO_SALT = 4e57693050da4345984d7d1360149032
```

---

### Step 3: Connect Domain (5 min)

**In Railway Dashboard:**
1. Go to Settings → Domains
2. Click **Custom Domain**
3. Enter: `khanjansevakendra.shop`
4. Copy the CNAME value provided

**In Your Domain Provider:**
```
Type: CNAME
Name: @
Value: (paste from Railway)
TTL: 600
```

---

### Step 4: Update Google OAuth (3 min)

Go to: https://console.cloud.google.com/apis/credentials

**Add these URLs:**
```
Authorized Redirect URIs:
  https://khanjansevakendra.shop/auth/callback

Authorized JavaScript Origins:
  https://khanjansevakendra.shop
```

**Save**

---

### Step 5: Update Instamojo Webhook (2 min)

Go to: https://www.instamojo.com/ → API & Plugins → Webhooks

```
Webhook URL: https://khanjansevakendra.shop/api/payments/webhook
Secret: 4e57693050da4345984d7d1360149032
```

---

### Step 6: Wait (5-30 min)

DNS propagation takes time. Check:
```bash
dig khanjansevakendra.shop
```

---

## ✅ Final URLs

| Page | URL |
|------|-----|
| 🏠 Home | https://khanjansevakendra.shop |
| 🔐 Login | https://khanjansevakendra.shop/login |
| 📊 Dashboard | https://khanjansevakendra.shop/dashboard |
| ⚙️ Admin | https://khanjansevakendra.shop/admin |
| 📚 API | https://khanjansevakendra.shop/api |

---

## 🧪 Test After Deployment

```bash
# Check if site is up
curl -I https://khanjansevakendra.shop

# Test health endpoint
curl https://khanjansevakendra.shop/health
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Domain not loading | Wait 30 min for DNS, check CNAME records |
| SSL error | Railway auto-SSL, wait 24 hours |
| Google login fails | Check redirect URI in Google Console |
| Payments not working | Check webhook URL in Instamojo |

---

## 📞 Need Help?

1. Check Railway logs: Dashboard → Deployments → Logs
2. Google OAuth issues: Check console.cloud.google.com
3. DNS issues: Check dnschecker.org

---

**Let's go live! 🚀**
