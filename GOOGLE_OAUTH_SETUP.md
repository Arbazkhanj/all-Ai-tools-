# Google OAuth Setup Guide

Is guide mein Google OAuth configure karne ka step-by-step process hai.

## Step 1: Google Cloud Console Pe Jao

1. [Google Cloud Console](https://console.cloud.google.com/) pe jao
2. Apna project select karo ya naya project banao

## Step 2: OAuth Consent Screen Setup

1. Left sidebar mein **"APIs & Services"** → **"OAuth consent screen"** pe jao
2. **User Type** select karo:
   - **External** - Koi bhi Google user login kar sakta hai
   - **Internal** - Sirf organization ke users
3. **Create** pe click karo

### App Information Fill Karo:
- **App name**: Khan Jan Seva Kendra
- **User support email**: Your email
- **App logo** (optional)
- **App domain**: http://localhost:7000 (for development)
- **Application home page**: http://localhost:7000
- **Application privacy policy link**: http://localhost:7000/privacy
- **Application terms of service link**: http://localhost:7000/terms
- **Developer contact information**: Your email
4. **Save and Continue**

## Step 3: Scopes Add Karo

1. **Add or Remove Scopes** pe click karo
2. Ye scopes add karo:
   - `openid`
   - `email`
   - `profile`
3. **Update** pe click karo
4. **Save and Continue**

## Step 4: Test Users Add Karo (For Development)

1. **Add Users** pe click karo
2. Apna email address add karo
3. **Add** pe click karo
4. **Save and Continue**

## Step 5: Credentials Create Karo

1. Left sidebar mein **"Credentials"** pe jao
2. **+ CREATE CREDENTIALS** → **OAuth client ID** select karo
3. **Application type**: Web application
4. **Name**: Khan Jan Seva Kendra Web

### Authorized JavaScript Origins Add Karo:
```
http://localhost
http://localhost:7000
```

### Authorized Redirect URIs Add Karo:
```
http://localhost:7000/auth/callback
```

**Note**: Production ke liye apna domain add karo:
```
https://yourdomain.com/auth/callback
```

5. **Create** pe click karo

## Step 6: Client ID aur Secret Copy Karo

1. **OAuth client created** popup mein se:
   - **Client ID** copy karo
   - **Client Secret** copy karo
2. **DOWNLOAD JSON** bhi kar lo (backup ke liye)
3. **OK** pe click karo

## Step 7: Environment Variables Set Karo

Terminal mein ye commands run karo:

```bash
export GOOGLE_CLIENT_ID='your-client-id-from-google-console'
export GOOGLE_CLIENT_SECRET='your-client-secret-from-google-console'
```

**Permanent** set karne ke liye `~/.zshrc` (Mac) ya `~/.bashrc` (Linux) mein add karo:

```bash
echo 'export GOOGLE_CLIENT_ID="your-client-id"' >> ~/.zshrc
echo 'export GOOGLE_CLIENT_SECRET="your-client-secret"' >> ~/.zshrc
source ~/.zshrc
```

## Step 8: Server Restart Karo

```bash
# Pehle existing process kill karo
kill $(lsof -t -i:7000) 2>/dev/null

# Phir server start karo
export GOOGLE_CLIENT_ID='your-client-id'
export GOOGLE_CLIENT_SECRET='your-client-secret'
rembg s --host 0.0.0.0 --port 7000
```

## Verification

1. Browser mein jao: http://localhost:7000/login
2. **"Continue with Google"** pe click karo
3. Apna Google account select karo
4. Agar "This app isn't verified" error aata hai, toh **Advanced** → **Go to Khan Jan Seva Kendra (unsafe)** pe click karo

## Production Deployment

Production ke liye:

1. **OAuth consent screen** → **PUBLISH APP** pe click karo
2. Authorized domains mein apna production domain add karo:
   - `https://yourdomain.com`
   - `https://www.yourdomain.com`
3. Redirect URIs update karo:
   - `https://yourdomain.com/auth/callback`
4. Environment variables production server pe set karo

## Troubleshooting

### Error: "redirect_uri_mismatch"
**Solution**: Google Console mein redirect URI exactly match hona chahiye. `http` vs `https` aur trailing slash `/` ka dhyan rakho.

### Error: "Access blocked: This app's request is invalid"
**Solution**: 
1. OAuth consent screen complete karo
2. Test users mein apna email add karo
3. Agar production hai, toh app ko publish karo

### Error: "Error 400: invalid_request"
**Solution**: `GOOGLE_CLIENT_ID` aur `GOOGLE_CLIENT_SECRET` sahi set hue hain ya nahi check karo:
```bash
echo $GOOGLE_CLIENT_ID
echo $GOOGLE_CLIENT_SECRET
```

## Support

Agar koi problem aati hai, toh:
1. Google Cloud Console mein **Monitoring** → **Logs** check karo
2. Terminal mein server logs check karo
3. http://localhost:7000/api pe API docs check karo
