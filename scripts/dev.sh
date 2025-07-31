#!/bin/bash

# Development startup script

set -e

echo "🔧 Starting Aura Backend in development mode..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Run database migrations if needed
echo "🗄️  Checking database migrations..."
if command -v supabase &> /dev/null; then
    # Check if supabase is initialized
    if [ -f "supabase/config.toml" ]; then
        echo "📊 Applying database migrations..."
        supabase db push
    else
        echo "⚠️  Supabase not initialized. Run: supabase init"
    fi
else
    echo "⚠️  Supabase CLI not found. Database migrations skipped."
fi

# Start the development server
echo "🚀 Starting FastAPI development server..."
python main.py