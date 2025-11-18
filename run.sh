#!/bin/bash

# German Tax Calculator Bot - Quick Start Script

set -e

echo "🇩🇪 German Tax Calculator Bot - Setup"
echo "====================================="

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  Configuration file not found!"
    echo ""
    echo "Creating .env from template..."
    cp .env.example .env
    echo ""
    echo "✅ .env file created"
    echo ""
    echo "📝 Please edit .env and add your:"
    echo "   - TELEGRAM_BOT_TOKEN"
    echo "   - ADMIN_TELEGRAM_ID"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt --upgrade

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting bot..."
echo ""

# Run the bot
python main.py
