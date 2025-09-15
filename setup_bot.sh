#!/bin/bash

echo "🎓 Grade 12 Results Checker - Telegram Bot Setup"
echo "================================================"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 first."
    exit 1
fi

echo "✅ pip3 found"

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv

if [ $? -eq 0 ]; then
    echo "✅ Virtual environment created"
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

# Check for bot token
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo ""
    echo "⚠️  TELEGRAM_BOT_TOKEN environment variable not set!"
    echo ""
    echo "To create a bot:"
    echo "1. Open Telegram and search for @BotFather"
    echo "2. Send /newbot command"
    echo "3. Choose a name for your bot"
    echo "4. Choose a username"
    echo "5. Copy the bot token"
    echo ""
    echo "Then set the environment variable:"
    echo "export TELEGRAM_BOT_TOKEN='your_bot_token_here'"
    echo ""
    echo "Or add it to your ~/.bashrc file:"
    echo "echo 'export TELEGRAM_BOT_TOKEN=\"your_bot_token_here\"' >> ~/.bashrc"
    echo "source ~/.bashrc"
    echo ""
    echo "After setting the token, run this script again."
    exit 1
fi

echo "✅ Bot token found"

# Test the bot
echo "🚀 Starting the bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

# Make sure we're in the virtual environment
source venv/bin/activate
python telegram_bot.py
