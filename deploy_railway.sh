#!/bin/bash

echo "🚀 Deploying Grade 12 Results Bot to Railway"
echo "============================================="

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📦 Initializing Git repository..."
    git init
    git add .
    git commit -m "Initial commit: Grade 12 Results Bot"
fi

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found!"
    echo ""
    echo "Please install Railway CLI:"
    echo "1. Go to https://railway.app"
    echo "2. Sign up with GitHub"
    echo "3. Install Railway CLI:"
    echo "   npm install -g @railway/cli"
    echo "   # OR"
    echo "   curl -fsSL https://railway.app/install.sh | sh"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Railway CLI found"

# Login to Railway
echo "🔐 Logging into Railway..."
railway login

# Create new project
echo "🏗️  Creating Railway project..."
railway init

# Set environment variable
echo "🔧 Setting environment variables..."
echo "Please enter your Telegram bot token:"
read -p "TELEGRAM_BOT_TOKEN: " BOT_TOKEN

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ Bot token is required!"
    exit 1
fi

railway variables set TELEGRAM_BOT_TOKEN="$BOT_TOKEN"

# Deploy
echo "🚀 Deploying to Railway..."
railway up

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Your bot is now online 24/7!"
echo "Check the Railway dashboard for logs and monitoring."
echo ""
echo "📱 Test your bot by sending /start to it on Telegram."
