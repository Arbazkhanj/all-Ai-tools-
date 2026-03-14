#!/bin/bash

echo "🚀 Khan Jan Seva Kendra - GitHub Push Script"
echo "============================================"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
fi

# Add all files
echo "📁 Adding files to git..."
git add .

# Commit
echo "💾 Committing changes..."
read -p "Enter commit message (or press Enter for default): " msg
if [ -z "$msg" ]; then
    msg="Production deployment setup"
fi
git commit -m "$msg"

# Check if remote exists
if ! git remote -v > /dev/null 2>&1; then
    echo ""
    echo "🔗 No remote repository configured!"
    echo ""
    echo "Create a GitHub repository first:"
    echo "  https://github.com/new"
    echo ""
    read -p "Enter your GitHub repository URL: " repo_url
    git remote add origin "$repo_url"
fi

# Push
echo ""
echo "⬆️  Pushing to GitHub..."
git push -u origin main || git push -u origin master

echo ""
echo "✅ Successfully pushed to GitHub!"
echo ""
echo "Next steps:"
echo "  1. Go to your GitHub repository"
echo "  2. Set up environment variables in your deployment platform"
echo "  3. Deploy the application"
echo ""
