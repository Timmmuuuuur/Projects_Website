#!/bin/bash
# Deployment script for PythonAnywhere

echo "🚀 Starting deployment..."

# Navigate to project directory
cd ~/Projects_Website

# Pull latest changes
echo "📥 Pulling from GitHub..."
git pull origin main

# Activate virtual environment
source myenv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt --quiet

# Collect static files
echo "🎨 Collecting static files..."
python manage.py collectstatic --noinput

# Run migrations
echo "🗄️ Running migrations..."
python manage.py migrate

# Touch reload file (if using web app reload file)
touch /var/www/dauletov_pythonanywhere_com_wsgi.py

echo "✅ Deployment complete! Your site is live."

