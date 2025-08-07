#!/bin/bash

# EdGPT Platform Deployment Script
# This script deploys the EdGPT platform to a production server

set -e  # Exit on any error

echo "🚀 Starting EdGPT Platform Deployment..."

# Configuration
APP_DIR="/var/www/edgpt"
SERVICE_USER="www-data"
PYTHON_VERSION="python3"
PORT="8094"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   print_error "This script must be run as root (use sudo)"
   exit 1
fi

print_status "Updating system packages..."
apt update && apt upgrade -y

print_status "Installing required packages..."
apt install -y python3 python3-pip python3-venv nginx supervisor sqlite3 certbot python3-certbot-nginx

print_status "Creating application directory..."
mkdir -p $APP_DIR
mkdir -p $APP_DIR/logs
mkdir -p $APP_DIR/static
mkdir -p $APP_DIR/templates

print_status "Copying application files..."
# Copy backend
cp -r backend/* $APP_DIR/
# Copy templates
cp -r templates/* $APP_DIR/templates/
# Copy static files
cp -r static/* $APP_DIR/static/ 2>/dev/null || true
# Copy assets
cp -r assets/* $APP_DIR/static/images/ 2>/dev/null || true

print_status "Setting up Python virtual environment..."
cd $APP_DIR
python3 -m venv venv
source venv/bin/activate

print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install Flask==2.3.3 Flask-CORS==4.0.0 gunicorn==21.2.0

print_status "Setting up database..."
python3 -c "
import sqlite3
import hashlib

# Initialize database
conn = sqlite3.connect('edgpt_platform.db')

# Create tables
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        website_url TEXT,
        business_name TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        is_admin BOOLEAN DEFAULT FALSE
    )
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS trial_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        website_url TEXT NOT NULL,
        business_name TEXT,
        phone TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending'
    )
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        domain TEXT NOT NULL,
        page_path TEXT NOT NULL,
        user_agent TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Create admin user
admin_email = 'admin@edgpt.ai'
admin_password = 'admin123'
admin_hash = hashlib.sha256(admin_password.encode()).hexdigest()

conn.execute('''
    INSERT OR IGNORE INTO users (email, password_hash, is_admin, business_name)
    VALUES (?, ?, ?, ?)
''', (admin_email, admin_hash, True, 'EdGPT Admin'))

conn.commit()
conn.close()
print('Database initialized successfully')
"

print_status "Setting up file permissions..."
chown -R $SERVICE_USER:$SERVICE_USER $APP_DIR
chmod +x $APP_DIR/app.py

print_status "Configuring Supervisor..."
cat > /etc/supervisor/conf.d/edgpt.conf << EOF
[program:edgpt]
command=$APP_DIR/venv/bin/gunicorn --bind 127.0.0.1:$PORT --workers 4 --timeout 120 app:app
directory=$APP_DIR
user=$SERVICE_USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=$APP_DIR/logs/app.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="$APP_DIR/venv/bin"
EOF

print_status "Configuring Nginx..."
cp config/nginx.conf /etc/nginx/sites-available/edgpt-domains
ln -sf /etc/nginx/sites-available/edgpt-domains /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

print_status "Testing Nginx configuration..."
nginx -t

print_status "Starting services..."
supervisorctl reread
supervisorctl update
supervisorctl start edgpt
systemctl restart nginx
systemctl enable supervisor
systemctl enable nginx

print_status "Setting up SSL certificates..."
print_warning "You need to run the following commands manually for each domain:"
echo "sudo certbot --nginx -d edgpt.ai -d www.edgpt.ai"
echo "sudo certbot --nginx -d gptsites.ai -d www.gptsites.ai"
echo "sudo certbot --nginx -d lawfirmgpt.ai -d www.lawfirmgpt.ai"
echo "sudo certbot --nginx -d cpafirm.ai -d www.cpafirm.ai"
echo "sudo certbot --nginx -d taxprepgpt.ai -d www.taxprepgpt.ai"
echo "sudo certbot --nginx -d businessbrokergpt.ai -d www.businessbrokergpt.ai"

print_status "Setting up automatic SSL renewal..."
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | crontab -

print_status "Checking application status..."
sleep 5
if supervisorctl status edgpt | grep -q "RUNNING"; then
    print_status "✅ EdGPT application is running successfully!"
else
    print_error "❌ EdGPT application failed to start. Check logs: $APP_DIR/logs/app.log"
    exit 1
fi

print_status "Checking Nginx status..."
if systemctl is-active --quiet nginx; then
    print_status "✅ Nginx is running successfully!"
else
    print_error "❌ Nginx failed to start. Check: sudo systemctl status nginx"
    exit 1
fi

print_status "🎉 Deployment completed successfully!"
echo ""
echo "📍 Application is running on port $PORT"
echo "📍 Logs are available at: $APP_DIR/logs/app.log"
echo "📍 Application directory: $APP_DIR"
echo ""
echo "🌐 Domains configured:"
echo "   • https://edgpt.ai"
echo "   • https://gptsites.ai"
echo "   • https://lawfirmgpt.ai"
echo "   • https://cpafirm.ai"
echo "   • https://taxprepgpt.ai"
echo "   • https://businessbrokergpt.ai"
echo ""
echo "🔧 Management commands:"
echo "   • Restart app: sudo supervisorctl restart edgpt"
echo "   • View logs: sudo tail -f $APP_DIR/logs/app.log"
echo "   • Check status: sudo supervisorctl status edgpt"
echo ""
print_warning "Don't forget to set up SSL certificates for all domains!"

