#!/bin/bash

# LLM Security Scanner Backend Setup Script

set -e

echo "🚀 Setting up LLM Security Scanner Backend..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your database credentials"
    read -p "Press Enter to continue after editing .env..."
fi

# Install dependencies
echo "📦 Installing dependencies..."
npm install

# Check MySQL connection
echo "🔍 Checking MySQL connection..."
source .env
if ! mysql -h "${DB_HOST:-localhost}" -u "${DB_USER:-root}" -p"${DB_PASSWORD}" -e "SELECT 1" 2>/dev/null; then
    echo "⚠️  Warning: Could not connect to MySQL"
    echo "Please ensure MySQL is running and credentials in .env are correct"
    read -p "Press Enter to continue anyway..."
fi

# Create database if it doesn't exist
echo "🗄️  Creating database if it doesn't exist..."
mysql -h "${DB_HOST:-localhost}" -u "${DB_USER:-root}" -p"${DB_PASSWORD}" <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME:-llm_scan_db};
EOF
echo "✓ Database ready"

# Run migrations
echo "🔄 Running database migrations..."
npm run migrate

# Ask about seeding
read -p "Do you want to seed the database with demo data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🌱 Seeding database..."
    npm run seed
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  npm run dev    # Development mode"
echo "  npm start      # Production mode"
echo ""
