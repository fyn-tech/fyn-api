#!/bin/bash

# Exit on error
set -e

echo "🚀 Setting up development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DEBUG=True
ENVIRONMENT=development
SECRET_KEY=dev-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
SESSION_COOKIE_DOMAIN=None
CSRF_COOKIE_DOMAIN=None
CSRF_TRUSTED_ORIGINS=http://localhost,http://127.0.0.1

# Database settings
DEV_DB_NAME=fyn_dev
DEV_DB_USER=postgres
DEV_DB_PASSWORD=postgres
DEV_DB_HOST=localhost
DEV_DB_PORT=5432
EOF
fi

# Setup PostgreSQL
echo "🐘 Setting up PostgreSQL..."
sudo -u postgres psql << EOF
ALTER USER postgres PASSWORD postgres;
CREATE DATABASE fyn_dev;
GRANT ALL PRIVILEGES ON DATABASE fyn_dev TO postgres;
EOF

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate

# Load fixture data
echo "🌱 Loading initial data..."
python manage.py loaddata initial_data

echo """
✅ Setup complete!

To activate the virtual environment:
source venv/bin/activate

To start development server:
python manage.py runserver
"""