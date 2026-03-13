# Google One Tap Sign-In Setup Guide
## Complete Implementation Instructions

---

## 📋 Table of Contents

1. [Get Google Client ID](#step-1-get-google-client-id)
2. [Frontend Integration](#step-2-frontend-integration)
3. [Backend Setup](#step-3-backend-setup)
4. [Testing](#step-4-testing)
5. [Security Best Practices](#security-best-practices)

---

## Step 1: Get Google Client ID

### 1.1 Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: `Khan Jan Seva Kendra`
4. Click **"Create"**

### 1.2 Enable Google Identity Services API

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google Identity Services"**
3. Click **"Enable"**

### 1.3 Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** (for public access) or **"Internal"** (for organization only)
3. Click **"Create"**
4. Fill in required fields:
   - **App name**: `Khan Jan Seva Kendra`
   - **User support email**: Your email
   - **Developer contact information**: Your email
5. Click **"Save and Continue"**
6. Skip **Scopes** and **Test users** for now
7. Click **"Back to Dashboard"**

### 1.4 Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ CREATE CREDENTIALS"** → **"OAuth client ID"**
3. Select **Application type**: `Web application`
4. Enter **Name**: `Khan Jan Seva Web Client`
5. Add **Authorized JavaScript origins**:
   ```
   http://localhost:7860
   http://127.0.0.1:7860
   https://yourdomain.com (for production)
   ```
6. Add **Authorized redirect URIs**:
   ```
   http://localhost:7860/auth/callback
   https://yourdomain.com/auth/callback (for production)
   ```
7. Click **"Create"**
8. **Copy the Client ID** (looks like: `123456789-abc123def456.apps.googleusercontent.com`)

### 1.5 Get Client Secret (Optional, for server-side flow)

After creating credentials, you'll see both:
- **Client ID** (public)
- **Client Secret** (keep private!)

Click **"Download JSON"** to save credentials.

---

## Step 2: Frontend Integration

### 2.1 Update HTML File

Edit `google_onetap.html` and replace:

```javascript
const GOOGLE_CLIENT_ID = 'YOUR_GOOGLE_CLIENT_ID.apps.googleusercontent.com';
```

With your actual Client ID:

```javascript
const GOOGLE_CLIENT_ID = '123456789-abc123def456.apps.googleusercontent.com';
```

### 2.2 Google One Tap Configuration Options

```javascript
google.accounts.id.initialize({
    client_id: GOOGLE_CLIENT_ID,
    callback: handleCredentialResponse,
    
    // Auto-select account if only one is available
    auto_select: true,  // or false
    
    // Cancel when clicking outside popup
    cancel_on_tap_outside: true,
    
    // Context text
    context: 'signin',  // 'signin' | 'signup' | 'use'
    
    // UI mode
    ux_mode: 'popup',   // 'popup' | 'redirect'
    
    // Allowed parent domains
    allowed_parent_origin: ['http://localhost:7860']
});
```

### 2.3 Button Customization

```javascript
google.accounts.id.renderButton(
    document.getElementById('g_id_signin'),
    { 
        theme: 'filled_blue',    // 'outline' | 'filled_blue' | 'filled_black'
        size: 'large',            // 'small' | 'medium' | 'large'
        width: '100%',
        text: 'signin_with',      // 'signin_with' | 'signup_with' | 'continue_with'
        shape: 'rectangular',     // 'rectangular' | 'pill' | 'circle' | 'square'
        logo_alignment: 'left'    // 'left' | 'center'
    }
);
```

---

## Step 3: Backend Setup

### Option A: Python (FastAPI)

#### Install Dependencies

```bash
pip install fastapi uvicorn google-auth python-jose
```

#### Set Environment Variables

```bash
export GOOGLE_CLIENT_ID="your-client-id.apps.googleusercontent.com"
export JWT_SECRET_KEY="your-secret-key"
```

#### Run Server

```bash
python backend_fastapi.py
```

Server runs on: `http://localhost:8000`

### Option B: Node.js (Express)

#### Install Dependencies

```bash
npm init -y
npm install express cors jsonwebtoken google-auth-library dotenv
```

#### Create .env file

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
JWT_SECRET=your-secret-key
PORT=8000
```

#### Run Server

```bash
node backend_nodejs.js
```

### Option C: PHP

#### Install Dependencies (using Composer)

```bash
composer require firebase/php-jwt google/apiclient
```

#### Configure Web Server

For Apache, create `.htaccess`:
```apache
RewriteEngine On
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule ^(.*)$ backend_php.php [QSA,L]
```

For Nginx:
```nginx
location / {
    try_files $uri $uri/ /backend_php.php?$query_string;
}
```

#### Run PHP Server

```bash
php -S localhost:8000 backend_php.php
```

---

## Step 4: Testing

### 4.1 Test Flow

1. Open frontend: `http://localhost:7860/google_onetap.html`
2. Google One Tap popup should appear automatically
3. Click **"Continue as [Your Name]"**
4. Check browser console for success message
5. Verify user data in backend

### 4.2 API Testing with curl

```bash
# Test health endpoint
curl http://localhost:8000/health

# Test authentication (replace TOKEN with actual JWT)
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/auth/me

# Test logout
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" http://localhost:8000/auth/logout
```

### 4.3 Check Users

**Python/FastAPI:**
```bash
curl http://localhost:8000/auth/users
```

**Node.js:**
```bash
curl http://localhost:8000/auth/users
```

**PHP:**
```bash
curl http://localhost:8000/auth/users
```

---

## 🔒 Security Best Practices

### 1. HTTPS in Production

Always use HTTPS in production:
```javascript
// Good
https://yourdomain.com

// Bad (only for local development)
http://localhost:7860
```

### 2. Store Secrets Securely

**Never hardcode secrets!** Use environment variables:

```bash
# .env file (add to .gitignore!)
GOOGLE_CLIENT_ID=xxx
JWT_SECRET_KEY=xxx
```

### 3. Validate Token Origin

```javascript
// Always verify the token's audience matches your Client ID
const payload = await ticket.getPayload();
if (payload.aud !== GOOGLE_CLIENT_ID) {
    throw new Error('Invalid audience');
}
```

### 4. Token Expiration

Set reasonable JWT expiration:
```javascript
// 24 hours is standard
const JWT_EXPIRATION = '24h';

// For sensitive apps, use shorter duration
const JWT_EXPIRATION = '1h';
```

### 5. CSRF Protection

For state parameter in OAuth:
```javascript
const state = crypto.randomBytes(32).toString('hex');
// Store in session and verify in callback
```

### 6. Content Security Policy

Add CSP headers to prevent XSS:
```html
<meta http-equiv="Content-Security-Policy" 
      content="script-src 'self' https://accounts.google.com https://apis.google.com;">
```

---

## 🐛 Troubleshooting

### Issue: "Invalid Client ID"

**Solution:**
1. Check Client ID is correct
2. Verify domain is in "Authorized JavaScript origins"
3. Clear browser cache

### Issue: "One Tap not showing"

**Solution:**
1. Check browser console for errors
2. Verify `allowed_parent_origin` matches your domain
3. User might have dismissed One Tap previously (reset in browser settings)

### Issue: "Token verification failed"

**Solution:**
1. Ensure `GOOGLE_CLIENT_ID` matches in both frontend and backend
2. Check system clock is synchronized
3. Token might be expired (get a fresh one)

### Issue: CORS errors

**Solution:**
1. Add your frontend domain to backend CORS whitelist
2. Ensure protocol matches (http vs https)

---

## 📚 Additional Resources

- [Google Identity Services Documentation](https://developers.google.com/identity/gsi/web)
- [OAuth 2.0 for Web Server Applications](https://developers.google.com/identity/protocols/oauth2/web-server)
- [JWT.io](https://jwt.io/) - Decode and debug JWT tokens

---

## ✅ Checklist

- [ ] Created Google Cloud Project
- [ ] Enabled Google Identity Services API
- [ ] Configured OAuth Consent Screen
- [ ] Created Web Application credentials
- [ ] Added authorized JavaScript origins
- [ ] Copied Client ID to frontend code
- [ ] Set up backend with JWT
- [ ] Tested login flow
- [ ] Configured HTTPS for production
- [ ] Secured environment variables

---

**You're all set!** 🎉 Users can now sign in with Google One Tap on your website.
