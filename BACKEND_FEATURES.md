# Backend Features - User Management, Wallet & Payments

This document describes the new backend features added to rembg for user management, wallet system, and payment processing.

## Features Overview

### 1. Free User Restrictions
- Background removal output limited to 480p resolution for non-logged in users
- Only basic AI models available (u2net, u2netp, u2net_human_seg, silueta)
- Watermark added to processed images for free users

### 2. Logged-in User Benefits
- HD background removal (up to 4K resolution)
- Access to all AI models (including advanced ones like BiRefNet, SAM, BRIA RMBG)
- Wallet system for tracking photo credits
- Processing history

### 3. Wallet System
- Each user gets a wallet with photo credits
- 1 credit = 1 photo processing
- Credits deducted automatically after successful processing
- Transaction history tracked

### 4. Pricing Plans
- **Basic**: ₹20 → 10 photos
- **Standard**: ₹50 → 30 photos (Save ₹10)
- **Premium**: ₹100 → 70 photos (Save ₹40)

### 5. Admin Controls
- View all users and their wallets
- View transaction history
- Enable/disable AI models
- Set models as basic (free) or advanced (paid)
- Add credits to user wallets manually
- Update pricing plans

## Database Schema

### Users Table
- `id`: Primary key
- `email`: User email (unique)
- `google_id`: Google OAuth ID
- `name`: User's display name
- `picture`: Profile picture URL
- `role`: User role (user/admin)
- `plan_type`: Free/Basic/Standard/Premium
- `plan_activated_at`: Plan activation timestamp
- `plan_expires_at`: Plan expiration timestamp
- `is_active`: Account status
- Timestamps: created_at, updated_at, last_login_at

### Wallet Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `balance`: Number of photo credits
- Timestamps: created_at, updated_at

### Wallet Transactions Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `amount`: Credit amount (+ for credit, - for debit)
- `transaction_type`: credit/debit/refund
- `status`: pending/completed/failed
- `description`: Transaction description
- `payment_id`: External payment reference
- `photo_usage_id`: Link to photo processing (if applicable)
- `created_at`: Transaction timestamp

### Photo Usage Table
- `id`: Primary key
- `user_id`: Foreign key to users
- `original_filename`: Original image filename
- `processed_at`: Processing timestamp
- `model_used`: AI model used
- `was_hd`: Whether HD processing was used
- `resolution`: Output resolution
- `credits_deducted`: Number of credits used

### Pricing Plans Table
- `id`: Primary key
- `name`: Plan identifier (basic/standard/premium)
- `display_name`: Human-readable name
- `price_inr`: Price in Indian Rupees
- `credits`: Number of photo credits
- `description`: Plan description
- `is_active`: Whether plan is available
- `allows_hd`: Whether HD processing is allowed
- `allows_all_models`: Whether all models are available

### Model Config Table
- `id`: Primary key
- `model_name`: AI model identifier
- `display_name`: Human-readable name
- `is_basic`: Whether available to free users
- `is_active`: Whether model is enabled
- `description`: Model description

## API Endpoints

### Authentication
- `GET /login` - Login page
- `GET /auth/google` - Google OAuth login
- `GET /auth/callback` - OAuth callback
- `GET /auth/logout` - Logout
- `GET /auth/me` - Get current user
- `POST /auth/google/token` - Google One Tap token verification

### User Dashboard
- `GET /api/user/profile` - Get user profile with wallet
- `GET /api/user/wallet` - Get wallet balance
- `GET /api/user/transactions` - Get transaction history
- `GET /api/user/photo-history` - Get photo processing history
- `GET /api/user/context` - Get user context with restrictions

### Payments & Plans
- `GET /api/plans` - Get available pricing plans
- `POST /api/plans/purchase` - Purchase a plan
- `POST /api/payments/verify` - Verify payment (Razorpay integration placeholder)

### Models
- `GET /api/models` - Get available models (filtered by user status)
- `GET /api/models/check` - Check if a model is allowed

### Background Removal (Updated)
- `GET /api/remove` - Remove background from URL
- `POST /api/remove` - Remove background from upload
  - Automatically applies restrictions based on user status
  - Deducts credits for logged-in users with active plans

### Admin Endpoints
- `GET /api/admin/users` - List all users
- `GET /api/admin/users/{id}` - Get user details
- `GET /api/admin/transactions` - List all transactions
- `POST /api/admin/users/{id}/add-credits` - Add credits to user
- `PUT /api/admin/plans/{name}` - Update pricing plan
- `POST /api/admin/models/{name}/toggle` - Enable/disable model
- `POST /api/admin/models/{name}/set-basic` - Set model access level
- `GET /api/admin/stats` - Get admin dashboard statistics

## Web Pages

- `/` - Main image processing interface
- `/login` - Login page with Google OAuth
- `/dashboard` - User dashboard (wallet, history, buy plans)
- `/admin` - Admin panel (users, transactions, models, plans)

## Security Features

1. **Backend-enforced restrictions**: All limitations are enforced server-side
2. **Session-based authentication**: Secure session management
3. **User context validation**: Every request validated for user permissions
4. **Model access control**: Model availability checked on every processing request
5. **Credit deduction**: Atomic operation with transaction logging

## Environment Variables

```bash
# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret

# Database
DATABASE_URL=sqlite:///./rembg_payments.db  # Default SQLite
# DATABASE_URL=postgresql://user:pass@localhost/rembg  # For PostgreSQL

# Razorpay (for payments)
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret
```

## First Admin Setup

To set a user as admin, run the following Python code:

```python
from rembg.backend.database import get_db_context
from rembg.backend.models import User, UserRole

with get_db_context() as db:
    user = db.query(User).filter(User.email == "admin@example.com").first()
    if user:
        user.role = UserRole.ADMIN
        db.commit()
        print(f"User {user.email} is now admin")
```

## Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
rembg s --host 0.0.0.0 --port 7000

# The database will be automatically initialized on first run
```

## Integration with Razorpay (Future)

The payment endpoints are prepared for Razorpay integration. To complete:

1. Set up Razorpay account and get API keys
2. Implement order creation endpoint
3. Implement payment verification webhook
4. Add frontend payment flow

See the `/api/payments/verify` endpoint for the verification placeholder.

## Default Pricing Plans

On first run, the following plans are automatically created:

| Plan | Price | Credits | Savings |
|------|-------|---------|---------|
| Basic | ₹20 | 10 | - |
| Standard | ₹50 | 30 | ₹10 |
| Premium | ₹100 | 70 | ₹40 |

## Default Model Configuration

Basic models (free users):
- u2net
- u2netp
- u2net_human_seg
- silueta

Advanced models (paid users only):
- isnet-general-use
- isnet-anime
- sam
- birefnet-* series
- bria-rmbg
- u2net_cloth_seg
