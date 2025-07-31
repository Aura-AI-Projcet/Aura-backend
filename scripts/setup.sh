#!/bin/bash

# Aura Backend Setup Script for WSL Environment

set -e

echo "🚀 Setting up Aura Backend Development Environment..."

# Check if we're in WSL
if grep -qi microsoft /proc/version; then
    echo "✅ WSL environment detected"
else
    echo "⚠️  Warning: This script is optimized for WSL"
fi

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Copy environment file
if [ ! -f .env ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your Supabase credentials"
fi

# Set executable permissions
chmod +x scripts/*.sh

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "🔧 Installing Supabase CLI..."
    # For WSL/Linux
    curl -sSf https://supabase.com/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

echo "✅ Setup completed!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your Supabase credentials"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python main.py"
echo "4. Or run with Docker: docker-compose up"