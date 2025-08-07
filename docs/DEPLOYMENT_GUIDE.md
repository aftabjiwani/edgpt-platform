# 🚀 EdGPT Platform Deployment Guide

This comprehensive guide covers deploying the EdGPT Platform across all 6 domains with proper SSL, domain routing, and production optimization.

## 📋 Prerequisites

### System Requirements
- **Ubuntu 20.04+ / CentOS 8+ / Debian 11+**
- **Python 3.8+**
- **4GB+ RAM** (8GB recommended for production)
- **20GB+ disk space**
- **Root or sudo access**

### Domain Requirements
- **6 domains** pointing to your server IP:
  - edgpt.ai
  - gptsites.ai
  - lawfirmgpt.ai
  - cpafirm.ai
  - taxprepgpt.ai
  - businessbrokergpt.ai

### Network Requirements
- **Port 80** (HTTP) - for SSL certificate generation
- **Port 443** (HTTPS) - for secure traffic
- **Port 22** (SSH) - for server management

## 🛠 Automated Deployment

### Quick Deployment (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/edgpt-platform.git
cd edgpt-platform
```

2. **Run the deployment script**
```bash
sudo ./scripts/deploy.sh
```

3. **Set up SSL certificates**
```bash
# For each domain, run:
sudo certbot --nginx -d edgpt.ai -d www.edgpt.ai
sudo certbot --nginx -d gptsites.ai -d www.gptsites.ai
sudo certbot --nginx -d lawfirmgpt.ai -d www.lawfirmgpt.ai
sudo certbot --nginx -d cpafirm.ai -d www.cpafirm.ai
sudo certbot --nginx -d taxprepgpt.ai -d www.taxprepgpt.ai
sudo certbot --nginx -d businessbrokergpt.ai -d www.businessbrokergpt.ai
```

4. **Verify deployment**
```bash
sudo supervisorctl status edgpt
curl -I https://edgpt.ai
```

## 🔧 Manual Deployment

### Step 1: System Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3 python3-pip python3-venv nginx supervisor sqlite3 certbot python3-certbot-nginx git

# Create application user
sudo useradd -r -s /bin/false edgpt
```

### Step 2: Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/edgpt
sudo chown edgpt:edgpt /var/www/edgpt

# Clone repository
cd /var/www/edgpt
sudo -u edgpt git clone https://github.com/yourusername/edgpt-platform.git .

# Set up Python environment
sudo -u edgpt python3 -m venv venv
sudo -u edgpt ./venv/bin/pip install --upgrade pip
sudo -u edgpt ./venv/bin/pip install -r requirements.txt
```

### Step 3: Database Initialization

```bash
cd /var/www/edgpt
sudo -u edgpt ./venv/bin/python3 -c "
import sqlite3
import hashlib
import os

# Create database
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
admin_password = 'admin123'  # Change this in production!
admin_hash = hashlib.sha256(admin_password.encode()).hexdigest()

conn.execute('''
    INSERT OR IGNORE INTO users (email, password_hash, is_admin, business_name)
    VALUES (?, ?, ?, ?)
''', (admin_email, admin_hash, True, 'EdGPT Admin'))

conn.commit()
conn.close()
print('Database initialized successfully')
"

# Set proper permissions
sudo chown edgpt:edgpt /var/www/edgpt/edgpt_platform.db
sudo chmod 644 /var/www/edgpt/edgpt_platform.db
```

### Step 4: Supervisor Configuration

```bash
sudo tee /etc/supervisor/conf.d/edgpt.conf > /dev/null << EOF
[program:edgpt]
command=/var/www/edgpt/venv/bin/gunicorn --bind 127.0.0.1:8094 --workers 4 --timeout 120 app:app
directory=/var/www/edgpt/backend
user=edgpt
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/www/edgpt/logs/app.log
stdout_logfile_maxbytes=50MB
stdout_logfile_backups=5
environment=PATH="/var/www/edgpt/venv/bin"
EOF

# Create logs directory
sudo mkdir -p /var/www/edgpt/logs
sudo chown edgpt:edgpt /var/www/edgpt/logs

# Start the application
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start edgpt
```

### Step 5: Nginx Configuration

```bash
# Copy Nginx configuration
sudo cp /var/www/edgpt/config/nginx.conf /etc/nginx/sites-available/edgpt-domains

# Enable the site
sudo ln -sf /etc/nginx/sites-available/edgpt-domains /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

### Step 6: SSL Certificate Setup

```bash
# Install certificates for all domains
domains=(
    "edgpt.ai www.edgpt.ai"
    "gptsites.ai www.gptsites.ai"
    "lawfirmgpt.ai www.lawfirmgpt.ai"
    "cpafirm.ai www.cpafirm.ai"
    "taxprepgpt.ai www.taxprepgpt.ai"
    "businessbrokergpt.ai www.businessbrokergpt.ai"
)

for domain_pair in "${domains[@]}"; do
    echo "Setting up SSL for: $domain_pair"
    sudo certbot --nginx -d $domain_pair --non-interactive --agree-tos --email admin@edgpt.ai
done

# Set up automatic renewal
(crontab -l 2>/dev/null; echo "0 12 * * * /usr/bin/certbot renew --quiet") | sudo crontab -
```

## 🔍 Verification & Testing

### Application Health Check

```bash
# Check application status
sudo supervisorctl status edgpt

# Check application logs
sudo tail -f /var/www/edgpt/logs/app.log

# Test application directly
curl -I http://localhost:8094/health
```

### Domain Testing

```bash
# Test all domains
domains=("edgpt.ai" "gptsites.ai" "lawfirmgpt.ai" "cpafirm.ai" "taxprepgpt.ai" "businessbrokergpt.ai")

for domain in "${domains[@]}"; do
    echo "Testing $domain..."
    curl -I "https://$domain"
    echo "---"
done
```

### SSL Certificate Verification

```bash
# Check SSL certificates
for domain in edgpt.ai gptsites.ai lawfirmgpt.ai cpafirm.ai taxprepgpt.ai businessbrokergpt.ai; do
    echo "SSL status for $domain:"
    echo | openssl s_client -servername $domain -connect $domain:443 2>/dev/null | openssl x509 -noout -dates
    echo "---"
done
```

## 🛡 Security Hardening

### Firewall Configuration

```bash
# Install and configure UFW
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable
```

### Application Security

```bash
# Change default admin password
cd /var/www/edgpt
sudo -u edgpt ./venv/bin/python3 -c "
import sqlite3
import hashlib
import getpass

# Get new password
new_password = getpass.getpass('Enter new admin password: ')
password_hash = hashlib.sha256(new_password.encode()).hexdigest()

# Update database
conn = sqlite3.connect('edgpt_platform.db')
conn.execute('UPDATE users SET password_hash = ? WHERE email = ?', 
             (password_hash, 'admin@edgpt.ai'))
conn.commit()
conn.close()
print('Admin password updated successfully')
"
```

### File Permissions

```bash
# Set secure file permissions
sudo find /var/www/edgpt -type f -exec chmod 644 {} \;
sudo find /var/www/edgpt -type d -exec chmod 755 {} \;
sudo chmod 600 /var/www/edgpt/edgpt_platform.db
sudo chmod +x /var/www/edgpt/backend/app.py
```

## 📊 Monitoring & Maintenance

### Log Monitoring

```bash
# Application logs
sudo tail -f /var/www/edgpt/logs/app.log

# Nginx access logs
sudo tail -f /var/log/nginx/access.log

# Nginx error logs
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u nginx -f
sudo journalctl -u supervisor -f
```

### Performance Monitoring

```bash
# Check system resources
htop
df -h
free -h

# Check application performance
sudo supervisorctl status
curl -w "@curl-format.txt" -o /dev/null -s "https://edgpt.ai"
```

### Backup Strategy

```bash
# Create backup script
sudo tee /usr/local/bin/edgpt-backup.sh > /dev/null << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/edgpt"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup database
cp /var/www/edgpt/edgpt_platform.db $BACKUP_DIR/edgpt_platform_$DATE.db

# Backup application files
tar -czf $BACKUP_DIR/edgpt_app_$DATE.tar.gz -C /var/www edgpt

# Keep only last 7 days of backups
find $BACKUP_DIR -name "*.db" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

sudo chmod +x /usr/local/bin/edgpt-backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /usr/local/bin/edgpt-backup.sh") | sudo crontab -
```

## 🔄 Updates & Maintenance

### Application Updates

```bash
# Pull latest changes
cd /var/www/edgpt
sudo -u edgpt git pull origin main

# Update dependencies
sudo -u edgpt ./venv/bin/pip install -r requirements.txt

# Restart application
sudo supervisorctl restart edgpt
```

### System Updates

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update SSL certificates
sudo certbot renew --dry-run
```

## 🚨 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
sudo tail -50 /var/www/edgpt/logs/app.log

# Check supervisor status
sudo supervisorctl status edgpt

# Restart application
sudo supervisorctl restart edgpt
```

#### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew --force-renewal

# Restart Nginx
sudo systemctl restart nginx
```

#### Database Issues
```bash
# Check database permissions
ls -la /var/www/edgpt/edgpt_platform.db

# Test database connection
cd /var/www/edgpt
sudo -u edgpt ./venv/bin/python3 -c "
import sqlite3
conn = sqlite3.connect('edgpt_platform.db')
print('Database connection successful')
conn.close()
"
```

#### Domain Routing Issues
```bash
# Test domain routing
curl -H "Host: edgpt.ai" http://localhost:8094/
curl -H "Host: gptsites.ai" http://localhost:8094/

# Check Nginx configuration
sudo nginx -t
sudo systemctl reload nginx
```

### Performance Issues

#### High CPU Usage
```bash
# Check processes
top -p $(pgrep -f gunicorn)

# Increase worker count
sudo nano /etc/supervisor/conf.d/edgpt.conf
# Change --workers 4 to --workers 8
sudo supervisorctl restart edgpt
```

#### High Memory Usage
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Restart application to clear memory
sudo supervisorctl restart edgpt
```

## 📞 Support

For deployment issues or questions:

- **Documentation**: [GitHub Repository](https://github.com/yourusername/edgpt-platform)
- **Issues**: [GitHub Issues](https://github.com/yourusername/edgpt-platform/issues)
- **Email**: support@edgpt.ai

---

**Deployment completed successfully! Your EdGPT Platform is now ready to serve all 6 domains with professional AI-powered experiences.** 🎉

