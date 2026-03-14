# Khan Jan Seva Kendra - AI Background Remover

AI-powered background removal service with user management, wallet system, and payment integration.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.11-green.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.128+-orange.svg)

## Features

- 🔐 **Google OAuth Authentication** - Secure login with Google
- 💰 **Wallet System** - Credit-based photo processing
- 💳 **Instamojo Payments** - Indian payment gateway integration
- 🤖 **AI Models** - Multiple background removal models
- 📊 **User Dashboard** - Track usage and transactions
- ⚙️ **Admin Panel** - Manage users, plans, and models
- 🔒 **Secure** - Backend-enforced restrictions

## Pricing Plans

| Plan | Price | Credits | Savings |
|------|-------|---------|---------|
| Basic | ₹20 | 10 | - |
| Standard | ₹50 | 30 | ₹10 |
| Premium | ₹100 | 70 | ₹40 |

## Tech Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite (development), PostgreSQL (production)
- **Auth**: Google OAuth 2.0
- **Payments**: Instamojo
- **AI**: ONNX Runtime, rembg library

## Quick Start

### Local Development

```bash
# Clone repository
git clone https://github.com/yourusername/khanjanseva.git
cd khanjanseva

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GOOGLE_CLIENT_SECRET='your-google-client-secret'
export SESSION_SECRET_KEY='your-random-secret-key'

# Run server
rembg s --host 0.0.0.0 --port 7000
```

Visit: http://localhost:7000

### Production Deployment

#### Option 1: Railway (Recommended)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/your-template)

1. Connect GitHub repository
2. Add environment variables
3. Auto-deploy on every push

#### Option 2: Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy)

1. Click "Deploy to Render"
2. Add environment variables
3. Deploy

#### Option 3: Heroku

```bash
heroku create your-app-name
heroku config:set GOOGLE_CLIENT_SECRET='your-secret'
git push heroku main
```

## Environment Variables

```env
# Required
GOOGLE_CLIENT_SECRET=your-google-client-secret
SESSION_SECRET_KEY=random-secret-key

# Payments (Instamojo)
INSTAMOJO_API_KEY=your-api-key
INSTAMOJO_AUTH_TOKEN=your-auth-token
INSTAMOJO_SALT=your-salt

# Optional
DATABASE_URL=sqlite:///./rembg_payments.db
```

## API Documentation

Once server is running, visit:
- API Docs: `http://localhost:7000/api`
- Health Check: `http://localhost:7000/health`

### Key Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/remove` | POST | Remove background from image |
| `/api/user/profile` | GET | Get user profile |
| `/api/user/wallet` | GET | Get wallet balance |
| `/api/plans` | GET | Get pricing plans |
| `/api/payments/create` | POST | Create payment |

## Project Structure

```
khanjanseva/
├── rembg/
│   ├── backend/          # Database, auth, payments
│   ├── commands/         # CLI commands
│   ├── sessions/         # AI models
│   └── static/           # HTML, CSS, JS
├── tests/                # Test files
├── requirements.txt      # Dependencies
├── Dockerfile           # Docker config
├── docker-compose.yml   # Docker compose
├── Procfile            # Heroku config
├── render.yaml         # Render config
└── railway.json        # Railway config
```

## Screenshots

### Main Interface
![Main](screenshots/main.png)

### Dashboard
![Dashboard](screenshots/dashboard.png)

### Admin Panel
![Admin](screenshots/admin.png)

## Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -am 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit pull request

## License

This project is licensed under the MIT License.

## Support

For support, email support@khanjanseva.com or create an issue.

---

Made with ❤️ by Khan Jan Seva Kendra
