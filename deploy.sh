#!/bin/bash
# Deployment script for PythonAnywhere
# IMPORTANT: This path must match your Web tab "Source code" directory on PythonAnywhere.
set -e

echo "🚀 Starting deployment..."

# Prefer REALWEBSITE path (common if you cloned there); fall back to ~/Projects_Website
PROJECT_DIR="${PA_PROJECT_DIR:-$HOME/REALWEBSITE/Projects_Website}"
if [ ! -f "$PROJECT_DIR/manage.py" ]; then
  PROJECT_DIR="$HOME/Projects_Website"
fi
if [ ! -f "$PROJECT_DIR/manage.py" ]; then
  echo "❌ Could not find manage.py. Set PA_PROJECT_DIR to your repo root, e.g.:"
  echo "   export PA_PROJECT_DIR=/home/YOURUSER/REALWEBSITE/Projects_Website"
  exit 1
fi

echo "📂 Using project directory: $PROJECT_DIR"
cd "$PROJECT_DIR"

# Pull latest changes
echo "📥 Pulling from GitHub..."
git pull origin main

# Activate virtual environment (create venv name to match your PA account)
VENV="${PA_VENV:-myenv}"
if [ -f "$PROJECT_DIR/$VENV/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$PROJECT_DIR/$VENV/bin/activate"
elif [ -f "$HOME/.virtualenvs/$(basename "$PROJECT_DIR")/bin/activate" ]; then
  # shellcheck source=/dev/null
  source "$HOME/.virtualenvs/$(basename "$PROJECT_DIR")/bin/activate"
else
  echo "❌ No venv found. Create one in the project folder or set PA_VENV=name"
  exit 1
fi

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

