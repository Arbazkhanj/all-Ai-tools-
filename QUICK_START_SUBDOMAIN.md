# 🚀 Quick Start: remove.khanjansevakendra.shop

**Your Setup:**
- Main Website: `https://khanjansevakendra.shop` (existing)
- Background Removal: `https://remove.khanjansevakendra.shop` (new)

---

## Step 1: GitHub Push (2 min)

```bash
cd /Users/arbaz/Downloads/rembg-main
./github_push.sh
```

---

## Step 2: Railway Deploy (5 min)

1. Go to https://railway.app/
2. **New Project** → **Deploy from GitHub**
3. Select repository
4. **Project name:** `remove-bg-service` (alag rakho)

### Add Environment Variables:
```
GOOGLE_CLIENT_SECRET=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
SESSION_SECRET_KEY=(run: openssl rand -hex 32)
INSTAMOJO_API_KEY=01c6b914d4f8e224cb4b6bdceaeb5b77
INSTAMOJO_AUTH_TOKEN=d8ea03ef36c426ab2c10891cabd03d8c
INSTAMOJO_SALT=4e57693050da4345984d7d1360149032
```

---

## Step 3: Domain Setup (5 min)

**Railway:** Settings → Domains → Custom Domain  
Enter: `remove.khanjansevakendra.shop`

**Copy the CNAME value**

---

## Step 4: GoDaddy DNS (3 min)

Login: https://dcc.godaddy.com/

**Add Record:**
```
Type: CNAME
Name: remove
Value: (paste Railway CNAME here)
TTL: 600
```

**Save**

---

## Step 5: Google OAuth (2 min)

https://console.cloud.google.com/apis/credentials

**Add Redirect URI:**
```
https://remove.khanjansevakendra.shop/auth/callback
```

**Add JavaScript Origin:**
```
https://remove.khanjansevakendra.shop
```

**Save**

---

## Step 6: Instamojo Webhook (2 min)

https://www.instamojo.com/ → API & Plugins → Webhooks

```
URL: https://remove.khanjansevakendra.shop/api/payments/webhook
Secret: 4e57693050da4345984d7d1360149032
```

---

## ✅ Done!

**Your URLs:**
- 🏠 Main: `https://khanjansevakendra.shop`
- 🖼️ Remove BG: `https://remove.khanjansevakendra.shop`
- 🔐 Login: `https://remove.khanjansevakendra.shop/login`
- 📊 Dashboard: `https://remove.khanjansevakendra.shop/dashboard`

---

## Link From Main Website

Apne main website `khanjansevakendra.shop` pe ye link add karo:

```html
<a href="https://remove.khanjansevakendra.shop">
  🖼️ Remove Image Background
</a>
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Subdomain not loading | Wait 30 min for DNS propagation |
| SSL error | Wait 24 hours for auto-SSL |
| Login fails | Check Google OAuth redirect URI |
| Payment fails | Check Instamojo webhook URL |

---

**Deploy Now! 🚀**
