#!/bin/bash

# ============================================================================
# KHAN JAN SEVA KENDRA - COMPLETE DEPLOYMENT SCRIPT
# This script will push to GitHub and guide Railway deployment
# ============================================================================

echo ""
echo "🚀 KHAN JAN SEVA KENDRA - COMPLETE DEPLOYMENT"
echo "=============================================="
echo ""
echo "Target: https://remove.khanjansevakendra.shop"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# STEP 1: CHECK REQUIREMENTS
# ============================================================================
echo -e "${BLUE}Step 1: Checking requirements...${NC}"

# Check git
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found! Install git first.${NC}"
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Not in project directory!${NC}"
    echo "Run this script from /Users/arbaz/Downloads/rembg-main"
    exit 1
fi

echo -e "${GREEN}✅ All requirements met${NC}"
echo ""

# ============================================================================
# STEP 2: GITHUB REPO SETUP
# ============================================================================
echo -e "${BLUE}Step 2: Setting up GitHub repository...${NC}"

# Initialize git if not already
if [ ! -d ".git" ]; then
    echo "Initializing git..."
    git init
fi

# Check if remote exists
if ! git remote -v > /dev/null 2>&1; then
    echo ""
    echo -e "${YELLOW}⚠️  No GitHub remote configured${NC}"
    echo ""
    echo "Create a GitHub repository first:"
    echo "  1. Go to: https://github.com/new"
    echo "  2. Repository name: khanjanseva-remove"
    echo "  3. Click 'Create repository'"
    echo ""
    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/khanjanseva-remove.git): " repo_url
    
    git remote add origin "$repo_url"
    echo -e "${GREEN}✅ Remote added${NC}"
fi

# Add all files
echo "Adding files to git..."
git add .

# Commit
echo "Creating commit..."
git commit -m "Deploy remove.khanjansevakendra.shop - AI Background Removal Service

Features:
- User authentication with Google OAuth
- Wallet system with credits
- Instamojo payment integration
- Multiple AI models for background removal
- Admin panel for management
- HD processing for paid users
- Free tier with 480p limitation

Domain: https://remove.khanjansevakendra.shop"

# Push to GitHub
echo ""
echo -e "${YELLOW}Pushing to GitHub...${NC}"
git push -u origin main || git push -u origin master

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Successfully pushed to GitHub!${NC}"
else
    echo -e "${RED}❌ GitHub push failed${NC}"
    echo "Check your credentials and try again"
    exit 1
fi

echo ""

# ============================================================================
# STEP 3: RAILWAY DEPLOYMENT INSTRUCTIONS
# ============================================================================
echo -e "${BLUE}Step 3: Railway Deployment${NC}"
echo ""
echo -e "${YELLOW}⚠️  I cannot directly deploy to Railway (requires login)${NC}"
echo ""
echo "Follow these exact steps:"
echo ""
echo "1. 🌐 Go to: https://railway.app/"
echo "   - Login with GitHub"
echo ""
echo "2. ➕ Click: 'New Project'"
echo "   - Select: 'Deploy from GitHub repo'"
echo "   - Choose: Your repository (khanjanseva-remove)"
echo ""
echo "3. ⚙️  Settings:"
echo "   - Project name: remove-bg-service"
echo "   - Click 'Deploy'"
echo ""
echo "4. 🔐 Add Environment Variables:"
echo "   Click 'Variables' tab, then add:"
echo ""
echo "   GOOGLE_CLIENT_SECRET=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"
echo "   SESSION_SECRET_KEY=$(openssl rand -hex 32)"
echo "   INSTAMOJO_API_KEY=01c6b914d4f8e224cb4b6bdceaeb5b77"
echo "   INSTAMOJO_AUTH_TOKEN=d8ea03ef36c426ab2c10891cabd03d8c"
echo "   INSTAMOJO_SALT=4e57693050da4345984d7d1360149032"
echo ""
read -p "Press Enter after adding environment variables..."
echo ""

# ============================================================================
# STEP 4: DOMAIN SETUP
# ============================================================================
echo -e "${BLUE}Step 4: Domain Setup${NC}"
echo ""
echo "In Railway Dashboard:"
echo ""
echo "1. 🌐 Click 'Settings' → 'Domains'"
echo "2. ➕ Click 'Custom Domain'"
echo "3. ✏️  Enter: remove.khanjansevakendra.shop"
echo "4. 📋 Copy the CNAME value shown"
echo ""
read -p "Press Enter after copying CNAME value..."
echo ""

# ============================================================================
# STEP 5: GODADDY DNS
# ============================================================================
echo -e "${BLUE}Step 5: GoDaddy DNS Configuration${NC}"
echo ""
echo "1. 🌐 Go to: https://dcc.godaddy.com/"
echo "2. 🔍 Find your domain: khanjansevakendra.shop"
echo "3. ⚙️  Click 'DNS'"
echo "4. ➕ Add new record:"
echo ""
echo "   Type: CNAME"
echo "   Name: remove"
echo "   Value: (paste Railway CNAME here)"
echo "   TTL: 600"
echo ""
echo "5. 💾 Save"
echo ""
read -p "Press Enter after adding DNS record..."
echo ""

# ============================================================================
# STEP 6: GOOGLE OAUTH
# ============================================================================
echo -e "${BLUE}Step 6: Google OAuth Update${NC}"
echo ""
echo "1. 🌐 Go to: https://console.cloud.google.com/apis/credentials"
echo "2. 📝 Click on your OAuth 2.0 Client ID"
echo "3. ➕ Add these URLs:"
echo ""
echo "   Authorized Redirect URIs:"
echo "   https://remove.khanjansevakendra.shop/auth/callback"
echo ""
echo "   Authorized JavaScript Origins:"
echo "   https://remove.khanjansevakendra.shop"
echo ""
echo "4. 💾 Save"
echo ""
read -p "Press Enter after updating Google OAuth..."
echo ""

# ============================================================================
# STEP 7: INSTAMOJO WEBHOOK
# ============================================================================
echo -e "${BLUE}Step 7: Instamojo Webhook${NC}"
echo ""
echo "1. 🌐 Go to: https://www.instamojo.com/"
echo "2. ⚙️  Go to: API & Plugins → Webhooks"
echo "3. ➕ Click 'New Webhook'"
echo ""
echo "   Webhook URL:"
echo "   https://remove.khanjansevakendra.shop/api/payments/webhook"
echo ""
echo "   Secret: 4e57693050da4345984d7d1360149032"
echo ""
echo "4. 💾 Save"
echo ""

# ============================================================================
# COMPLETION
# ============================================================================
echo ""
echo "=============================================="
echo -e "${GREEN}🎉 DEPLOYMENT COMPLETE!${NC}"
echo "=============================================="
echo ""
echo "Your websites:"
echo ""
echo "🏠 Main:     https://khanjansevakendra.shop"
echo "🖼️  Remove BG: https://remove.khanjansevakendra.shop"
echo ""
echo "⏳ DNS propagation may take 5-30 minutes"
echo ""
echo "✅ Check your site:"
echo "   curl -I https://remove.khanjansevakendra.shop"
echo ""
echo "📚 Documentation:"
echo "   - SUBDOMAIN_SETUP.md"
echo "   - QUICK_START_SUBDOMAIN.md"
echo ""
echo "🚀 Good luck!"
echo ""
