# Instamojo Webhook Setup Guide

## Step 1: Webhook URL Generate Karo

### Local Testing Ke Liye (ngrok use karo)

**Option A: Ngrok (Recommended for local testing)**

1. **Ngrok Install Karo:**
```bash
# MacOS
brew install ngrok

# Ya download karo: https://ngrok.com/download
```

2. **Ngrok Account Banao:**
   - https://ngrok.com/ pe jao
   - Free account banao
   - Auth token copy karo

3. **Ngrok Configure Karo:**
```bash
ngrok config add-authtoken YOUR_AUTH_TOKEN
```

4. **Ngrok Start Karo (Port 7002 ke liye):**
```bash
ngrok http 7002
```

5. **Webhook URL Copy Karo:**
Output mein milega:
```
Forwarding: https://abcd1234.ngrok.io -> http://localhost:7002
```

**Webhook URL:** `https://abcd1234.ngrok.io/api/payments/webhook`

---

### Production Ke Liye

**Webhook URL:** `https://yourdomain.com/api/payments/webhook`

Example:
- `https://khanjanseva.com/api/payments/webhook`
- `https://api.khanjanseva.com/api/payments/webhook`

---

## Step 2: Instamojo Dashboard Mein Webhook Configure Karo

1. **Instamojo Dashboard** pe jao: https://www.instamojo.com/

2. **API & Plugins** → **Webhooks** pe click karo

3. **New Webhook** add karo:

   | Field | Value |
   |-------|-------|
   | **Webhook URL** | `https://your-ngrok-url.ngrok.io/api/payments/webhook` (local) OR `https://yourdomain.com/api/payments/webhook` (production) |
   | **Secret** | `4e57693050da4345984d7d1360149032` |
   | **Events** | Select All (Payment.success, Payment.failed, etc.) |

4. **Save** karo

---

## Step 3: Webhook Secret/Signature Verify Karo

### Instamojo Webhook Payload Example:

```json
{
  "amount": "20.00",
  "buyer": "test@example.com",
  "buyer_name": "Test User",
  "buyer_phone": "+919999999999",
  "currency": "INR",
  "fees": "0.40",
  "longurl": "https://www.instamojo.com/@khanjansevakendra/...",
  "mac": "generated_signature_here",
  "payment_id": "MOJO123456789",
  "payment_request_id": "pr_id_here",
  "purpose": "Basic Plan - 10 Credits",
  "shorturl": "https://imjo.in/abc123",
  "status": "Credit",
  "custom_user_id": "1",
  "custom_plan_name": "basic",
  "custom_order_id": "uuid_here"
}
```

### MAC (Signature) Verification:

Instamojo signature (`mac`) ko verify karne ke liye:

```python
import hashlib
import hmac

def verify_webhook(data, mac, salt="4e57693050da4345984d7d1360149032"):
    """Verify Instamojo webhook signature."""
    # Create message string (sorted keys, pipe separated)
    sorted_keys = sorted(data.keys())
    message = "|".join(str(data[key]) for key in sorted_keys if key != "mac")
    
    # Generate MAC using HMAC-SHA1
    generated_mac = hmac.new(
        salt.encode(),
        message.encode(),
        hashlib.sha1
    ).hexdigest()
    
    # Compare MACs
    return hmac.compare_digest(generated_mac, mac)
```

---

## Step 4: Webhook Test Karo

### Method 1: Using Instamojo Dashboard

1. **Instamojo Dashboard** → **Payment Links**
2. Test payment link create karo
3. Payment complete karo (test mode mein)
4. Webhook automatically trigger hoga

### Method 2: Manual Test (curl)

```bash
curl -X POST http://localhost:7002/api/payments/webhook \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "amount=20.00" \
  -d "buyer=test@example.com" \
  -d "buyer_name=Test User" \
  -d "currency=INR" \
  -d "fees=0.40" \
  -d "payment_id=MOJO123456789" \
  -d "payment_request_id=pr_test_123" \
  -d "purpose=Basic Plan - 10 Credits" \
  -d "status=Credit" \
  -d "custom_user_id=1" \
  -d "custom_plan_name=basic" \
  -d "mac=calculated_mac_here"
```

### Method 3: Python Script

```python
import requests

# Test webhook
webhook_data = {
    "amount": "20.00",
    "buyer": "test@example.com",
    "buyer_name": "Test User",
    "currency": "INR",
    "fees": "0.40",
    "payment_id": "MOJO123456789",
    "payment_request_id": "pr_test_123",
    "purpose": "Basic Plan - 10 Credits",
    "status": "Credit",
    "custom_user_id": "1",
    "custom_plan_name": "basic",
    "custom_order_id": "test-order-123",
    "mac": "test_mac_for_development"
}

response = requests.post(
    "http://localhost:7002/api/payments/webhook",
    data=webhook_data
)
print(response.json())
```

---

## Step 5: Webhook Logs Check Karo

### Server Logs:
```bash
# Terminal mein server logs dekho
# Successful webhook ka log:
# INFO: Payment webhook received for user_id=1, plan=basic
# INFO: Credits added: 10, New balance: 10
```

### Database Check:
```bash
# SQLite database check karo
sqlite3 rembg_payments.db "SELECT * FROM wallet_transactions ORDER BY id DESC LIMIT 5;"
```

---

## Important: Webhook Security

### 1. Always Verify MAC Signature
```python
# Backend code (already implemented)
mac = data.get("mac", "")
if not verify_webhook(data, mac):
    return {"success": False, "message": "Invalid signature"}
```

### 2. Use HTTPS in Production
- Local testing: ngrok provides HTTPS
- Production: SSL certificate required

### 3. Webhook Retry Logic
Instamojo agar webhook fail hota hai toh retry karta hai:
- 3 retries with exponential backoff
- Agar sab fail ho jaye toh manual check karna padega

### 4. Idempotency Handle Karo
Same payment webhook do baar aa sakta hai:
```python
# Check if payment already processed
existing = db.query(WalletTransaction).filter_by(
    payment_id=payment_id
).first()

if existing:
    return {"success": True, "message": "Already processed"}
```

---

## Troubleshooting

### Webhook Not Receiving

1. **Ngrok Check:**
```bash
# Ngrok running hai?
curl http://localhost:4040/api/tunnels
```

2. **URL Check:**
```bash
# Webhook URL accessible hai?
curl -I https://your-ngrok-url.ngrok.io/health
```

3. **Firewall Check:**
```bash
# Port 7002 open hai?
netstat -an | grep 7002
```

### Signature Verification Failed

1. **Salt Check:** Instamojo dashboard mein jo salt hai wahi use karo
2. **Key Sorting:** Keys alphabetical order mein sort honi chahiye
3. **Data Types:** All values string format mein honi chahiye

### Credits Not Adding

1. **Custom Fields Check:** `custom_user_id` aur `custom_plan_name` present honi chahiye
2. **Status Check:** Sirf `Credit` status pe credits add honge
3. **Database Check:** User aur plan database mein exist karte hain?

---

## Quick Start Commands

```bash
# Terminal 1: Start Server
GOOGLE_CLIENT_SECRET='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' rembg s --host 0.0.0.0 --port 7002

# Terminal 2: Start Ngrok (new tab)
ngrok http 7002

# Copy ngrok HTTPS URL and add to Instamojo dashboard
# Example: https://abcd1234.ngrok.io/api/payments/webhook

# Test payment from dashboard
# Check server logs for webhook
```

---

## Webhook URL Format Summary

| Environment | Webhook URL Example |
|-------------|-------------------|
| Local (ngrok) | `https://abcd1234.ngrok.io/api/payments/webhook` |
| Production | `https://khanjanseva.com/api/payments/webhook` |
| Test Server | `https://test.khanjanseva.com/api/payments/webhook` |

---

## Secret/Salt Summary

| Purpose | Value |
|---------|-------|
| **Webhook Verification Salt** | `4e57693050da4345984d7d1360149032` |
| **API Key** | `01c6b914d4f8e224cb4b6bdceaeb5b77` |
| **Auth Token** | `d8ea03ef36c426ab2c10891cabd03d8c` |

---

Need help? Instamojo support: support@instamojo.com
