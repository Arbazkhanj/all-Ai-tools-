# Instamojo Payment Integration

Payment gateway Instamojo ke through integrate ho gaya hai.

## API Keys (Already Configured)

```
API Key: 01c6b914d4f8e224cb4b6bdceaeb5b77
Auth Token: d8ea03ef36c426ab2c10891cabd03d8c
Salt: 4e57693050da4345984d7d1360149032
Account: khanjansevakendra
```

## How It Works

### 1. User Dashboard
- User login karega
- Dashboard pe wallet balance aur plans dikhayega
- "Recharge Wallet" pe click karega

### 2. Payment Flow
```
1. User Plan Select karega (Basic/Standard/Premium)
2. Backend Instamojo payment link create karega
3. User Instamojo payment page pe redirect hoga
4. Payment successful hone pe wapas dashboard pe aayega
5. Credits automatically wallet mein add ho jayenge
```

### 3. API Endpoints

**Create Payment:**
```bash
POST /api/payments/create?plan_name=basic
```
Response:
```json
{
  "success": true,
  "payment_url": "https://www.instamojo.com/@khanjansevakendra/...",
  "payment_request_id": "pr_id_here",
  "order_id": "uuid_here"
}
```

**Check Payment Status:**
```bash
GET /api/payments/status/{payment_request_id}
```

**Webhook (Auto):**
```bash
POST /api/payments/webhook
```
- Instamojo automatically webhook bhejta hai payment complete hone pe
- Webhook se credits automatically add ho jate hain

## Testing

### Manual Payment Link Create Karo:

```python
from rembg.backend.payments import payment_service
from rembg.backend.database import get_db_context
from rembg.backend.services import PlanService

with get_db_context() as db:
    # Get user and plan
    user = db.query(User).filter(User.email == "test@example.com").first()
    plan = PlanService.get_plan_by_name(db, "basic")
    
    # Create payment
    success, result = payment_service.create_plan_purchase_payment(
        db=db,
        user=user,
        plan=plan,
        redirect_url="http://localhost:7002/dashboard"
    )
    
    if success:
        print(f"Payment URL: {result['payment_url']}")
```

## Webhook Setup (Important)

Instamojo dashboard mein webhook configure karo:

1. **Instamojo Dashboard** → **API & Plugins** → **Webhooks**
2. **Webhook URL** add karo:
   ```
   https://yourdomain.com/api/payments/webhook
   ```
   Development ke liye:
   ```
   http://localhost:7002/api/payments/webhook
   ```
3. **Secret** field mein salt daalo: `4e57693050da4345984d7d1360149032`

## Pricing Plans

| Plan | Price | Credits | Savings |
|------|-------|---------|---------|
| Basic | ₹20 | 10 | - |
| Standard | ₹50 | 30 | ₹10 |
| Premium | ₹100 | 70 | ₹40 |

## Troubleshooting

### Payment Link Create Nahi Ho Raha
Check karo API keys sahi hain:
```bash
curl -X GET \
  -H "X-Api-Key: 01c6b914d4f8e224cb4b6bdceaeb5b77" \
  -H "X-Auth-Token: d8ea03ef36c426ab2c10891cabd03d8c" \
  https://www.instamojo.com/api/1.1/payment-requests/
```

### Webhook Kaam Nahi Kar Raha
- Instamojo dashboard mein webhook URL check karo
- Server logs check karo: `tail -f /var/log/rembg.log`
- Webhook signature verify ho raha hai ya nahi check karo

### Credits Add Nahi Ho Rahe
- Database check karo: `wallet` table mein balance update hua hai ya nahi
- `wallet_transactions` table check karo
- Payment status check karo API se

## Going Live

Production deployment ke liye:

1. **Instamojo Account Verify Karo**
   - KYC complete karo
   - Bank account link karo

2. **Environment Variables Set Karo**
   ```bash
   export INSTAMOJO_MODE=production
   export INSTAMOJO_API_KEY=your_live_key
   export INSTAMOJO_AUTH_TOKEN=your_live_token
   export INSTAMOJO_SALT=your_live_salt
   ```

3. **Webhook URL Update Karo**
   ```
   https://yourdomain.com/api/payments/webhook
   ```

4. **Test Transactions**
   - Pehle small amount se test karo (₹10)
   - Webhook logs check karo
   - Credits properly add ho rahe hain verify karo

## Support

Instamojo Support:
- Website: https://www.instamojo.com/
- API Docs: https://docs.instamojo.com/
- Support Email: support@instamojo.com
