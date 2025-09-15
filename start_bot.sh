#!/bin/bash

echo "🚀 Starting Grade 12 Results Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup_bot.sh first."
    exit 1
fi

# Check if bot token is set
if [ -z "$TELEGRAM_BOT_TOKEN" ]; then
    echo "❌ TELEGRAM_BOT_TOKEN environment variable not set!"
    echo "Please set it with: export TELEGRAM_BOT_TOKEN='your_bot_token_here'"
    exit 1
fi

# Activate virtual environment and start bot
echo "🔄 Activating virtual environment..."
source venv/bin/activate

echo "🤖 Starting bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

python telegram_bot.py
