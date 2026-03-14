#!/bin/bash

# Khan Jan Seva Kendra - Server Startup Script

echo "🚀 Starting Khan Jan Seva Kendra Server..."
echo ""

# Check for Google OAuth Client Secret
if [ -z "$GOOGLE_CLIENT_SECRET" ]; then
    echo "❌ ERROR: GOOGLE_CLIENT_SECRET environment variable is not set!"
    echo ""
    echo "To fix this:"
    echo ""
    echo "1. Go to https://console.cloud.google.com/apis/credentials"
    echo "2. Click on your OAuth 2.0 Client ID"
    echo "3. Copy the Client Secret"
    echo "4. Run: export GOOGLE_CLIENT_SECRET='your-client-secret'"
    echo ""
    exit 1
fi

echo "✅ Google OAuth configured"
echo "✅ Client ID: 894379656916-rtiufltvtpemq1fu8mpi0guq5hm486lc.apps.googleusercontent.com"
echo "✅ Starting server on http://localhost:7000"
echo ""

# Kill any existing process on port 7000
echo "🧹 Cleaning up existing processes..."
lsof -ti:7000 | xargs kill -9 2>/dev/null

# Start the server
rembg s --host 0.0.0.0 --port 7000
