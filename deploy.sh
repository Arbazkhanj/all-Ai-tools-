#!/bin/bash
# Khan Jan Seva Kendra - Deployment Script
# Usage: ./deploy.sh [platform]
# Platforms: railway, render, docker

set -e

PLATFORM=${1:-"railway"}

echo "=========================================="
echo "🚀 Khan Jan Seva Kendra Deployment"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

case $PLATFORM in
  railway)
    echo -e "${BLUE}Deploying to Railway...${NC}"
    echo ""
    
    # Check if railway CLI is installed
    if ! command -v railway &> /dev/null; then
      echo "Installing Railway CLI..."
      npm install -g @railway/cli
    fi
    
    # Check if logged in
    railway whoami || railway login
    
    # Initialize if not already
    if [ ! -f .railway/config.json ]; then
      echo "Initializing Railway project..."
      railway init
    fi
    
    # Deploy
    echo "Deploying..."
    railway up
    
    echo ""
    echo -e "${GREEN}✅ Deployed to Railway!${NC}"
    echo -e "${YELLOW}Visit your dashboard to see the URL${NC}"
    ;;
    
  render)
    echo -e "${BLUE}Deploying to Render...${NC}"
    echo ""
    echo "Pushing to GitHub first..."
    git add .
    git commit -m "Ready for Render deployment" || true
    git push origin main || true
    
    echo ""
    echo -e "${GREEN}✅ Code pushed to GitHub!${NC}"
    echo -e "${YELLOW}Now go to https://render.com and create a new Web Service${NC}"
    echo ""
    echo "Settings:"
    echo "  - Build Command: pip install -r requirements.txt"
    echo "  - Start Command: rembg s --host 0.0.0.0 --port \$PORT"
    ;;
    
  docker)
    echo -e "${BLUE}Building Docker image...${NC}"
    echo ""
    
    docker build -t khan-jan-seva .
    
    echo ""
    echo -e "${GREEN}✅ Docker image built!${NC}"
    echo ""
    echo "Run with:"
    echo "  docker run -p 7860:7860 -e GOOGLE_CLIENT_ID=xxx -e GOOGLE_CLIENT_SECRET=xxx khan-jan-seva"
    ;;
    
  *)
    echo "Usage: ./deploy.sh [railway|render|docker]"
    echo ""
    echo "Examples:"
    echo "  ./deploy.sh railway    # Deploy to Railway (Recommended)"
    echo "  ./deploy.sh render     # Deploy to Render"
    echo "  ./deploy.sh docker     # Build Docker image"
    exit 1
    ;;
esac

echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
