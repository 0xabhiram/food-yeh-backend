# Digital Ocean Deployment Guide

## Overview
This guide covers deploying your FastAPI backend and MQTT server to a Digital Ocean droplet for production use.

## Prerequisites
- Digital Ocean account
- Domain name (optional but recommended)
- SSH key configured

## Step 1: Create Digital Ocean Droplet

### 1.1 Create Droplet
1. Log into Digital Ocean
2. Click "Create" → "Droplets"
3. Choose configuration:
   - **Distribution**: Ubuntu 22.04 LTS
   - **Plan**: Basic (2GB RAM, 1 CPU minimum)
   - **Datacenter**: Choose closest to your users
   - **Authentication**: SSH Key (recommended) or Password
   - **Hostname**: `foodyeh-backend`

### 1.2 Initial Server Setup
```bash
# Connect to your droplet
ssh root@YOUR_DROPLET_IP

# Update system
apt update && apt upgrade -y

# Create non-root user
adduser foodyeh
usermod -aG sudo foodyeh

# Switch to new user
su - foodyeh
```

## Step 2: Install Dependencies

### 2.1 Install Python and System Dependencies
```bash
# Update package list
sudo apt update

# Install Python 3.11 and pip
sudo apt install python3.11 python3.11-pip python3.11-venv -y

# Install system dependencies
sudo apt install nginx supervisor redis-server mosquitto mosquitto-clients -y

# Install additional dependencies
sudo apt install git curl wget unzip -y
```

### 2.2 Install Node.js (for PM2 if needed)
```bash
# Install Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Install PM2 globally
sudo npm install -g pm2
```

## Step 3: Setup Project Structure

### 3.1 Clone/Create Project
```bash
# Create project directory
mkdir -p /home/foodyeh/foodyeh-backend
cd /home/foodyeh/foodyeh-backend

# If using git
git clone YOUR_REPOSITORY_URL .

# Or create project structure manually
mkdir -p backend frontend
```

### 3.2 Setup Python Environment
```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install fastapi uvicorn[standard] python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv redis paho-mqtt sqlalchemy psycopg2-binary alembic
```

## Step 4: Configure Environment Variables

### 4.1 Create Environment File
```bash
# Create .env file
nano .env
```

Add the following configuration:
```env
# Database Configuration
DATABASE_URL=postgresql://foodyeh:your_password@localhost:5432/foodyeh_db

# JWT Configuration
SECRET_KEY=your_super_secret_key_here_make_it_long_and_random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# MQTT Configuration
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=admin
MQTT_PASSWORD=your_mqtt_password

# Redis Configuration
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
ENFORCE_HTTPS=true

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=3600

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/foodyeh/app.log

# CORS
ALLOWED_ORIGINS=["https://your-domain.com", "https://admin.your-domain.com"]

# Admin Configuration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_admin_password
ADMIN_EMAIL=admin@foodyeh.io
```

### 4.2 Setup Database
```bash
# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql
```

In PostgreSQL prompt:
```sql
CREATE DATABASE foodyeh_db;
CREATE USER foodyeh WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE foodyeh_db TO foodyeh;
ALTER USER foodyeh CREATEDB;
\q
```

## Step 5: Configure MQTT Server

### 5.1 Configure Mosquitto
```bash
# Create MQTT configuration
sudo nano /etc/mosquitto/mosquitto.conf
```

Add configuration:
```conf
# Basic configuration
port 1883
protocol mqtt

# Security
allow_anonymous false
password_file /etc/mosquitto/passwd

# Persistence
persistence true
persistence_location /var/lib/mosquitto/

# Logging
log_dest file /var/log/mosquitto/mosquitto.log
log_type all
log_timestamp true

# WebSocket support (optional)
listener 9001
protocol websockets
```

### 5.2 Create MQTT Users
```bash
# Create password file
sudo mosquitto_passwd -c /etc/mosquitto/passwd admin

# Set proper permissions
sudo chown mosquitto:mosquitto /etc/mosquitto/passwd
sudo chmod 600 /etc/mosquitto/passwd

# Restart Mosquitto
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto
```

## Step 6: Configure Nginx

### 6.1 Create Nginx Configuration
```bash
# Create site configuration
sudo nano /etc/nginx/sites-available/foodyeh
```

Add configuration:
```nginx
server {
    listen 80;
    server_name your-domain.com api.your-domain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com api.your-domain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # SSL Security
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    
    # API Proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }
    
    # Health check
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files (if any)
    location /static/ {
        alias /home/foodyeh/foodyeh-backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
}
```

### 6.2 Enable Site
```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/foodyeh /etc/nginx/sites-enabled/

# Remove default site
sudo rm /etc/nginx/sites-enabled/default

# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## Step 7: Setup SSL Certificate

### 7.1 Install Certbot
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d api.your-domain.com

# Setup auto-renewal
sudo crontab -e
```

Add to crontab:
```
0 12 * * * /usr/bin/certbot renew --quiet
```

## Step 8: Configure Supervisor

### 8.1 Create Supervisor Configuration
```bash
# Create supervisor config
sudo nano /etc/supervisor/conf.d/foodyeh.conf
```

Add configuration:
```ini
[program:foodyeh-api]
command=/home/foodyeh/foodyeh-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/home/foodyeh/foodyeh-backend
user=foodyeh
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/foodyeh/api.log
environment=PYTHONPATH="/home/foodyeh/foodyeh-backend"

[program:foodyeh-mqtt]
command=/home/foodyeh/foodyeh-backend/venv/bin/python mqtt_client.py
directory=/home/foodyeh/foodyeh-backend
user=foodyeh
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/foodyeh/mqtt.log
environment=PYTHONPATH="/home/foodyeh/foodyeh-backend"
```

### 8.2 Setup Logging
```bash
# Create log directory
sudo mkdir -p /var/log/foodyeh
sudo chown foodyeh:foodyeh /var/log/foodyeh

# Reload supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start foodyeh-api
sudo supervisorctl start foodyeh-mqtt
```

## Step 9: Configure Firewall

### 9.1 Setup UFW Firewall
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow ssh

# Allow HTTP/HTTPS
sudo ufw allow 80
sudo ufw allow 443

# Allow MQTT (if external access needed)
sudo ufw allow 1883

# Allow WebSocket (if needed)
sudo ufw allow 9001

# Check status
sudo ufw status
```

## Step 10: Setup Monitoring

### 10.1 Install Monitoring Tools
```bash
# Install htop for system monitoring
sudo apt install htop -y

# Install logrotate
sudo apt install logrotate -y
```

### 10.2 Create Logrotate Configuration
```bash
# Create logrotate config
sudo nano /etc/logrotate.d/foodyeh
```

Add configuration:
```
/var/log/foodyeh/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 foodyeh foodyeh
    postrotate
        supervisorctl restart foodyeh-api
        supervisorctl restart foodyeh-mqtt
    endscript
}
```

## Step 11: Update Flutter App Configuration

### 11.1 Update API Base URL
In your Flutter app, update the API base URL in `lib/core/constants/app_constants.dart`:

```dart
// Production API URL
static const String baseUrl = 'https://api.your-domain.com';
```

### 11.2 Update MQTT Configuration
If your Flutter app needs direct MQTT access, update the MQTT broker URL:

```dart
// MQTT Configuration
static const String mqttBroker = 'mqtt.your-domain.com';
static const int mqttPort = 1883;
```

## Step 12: Testing and Verification

### 12.1 Test API Endpoints
```bash
# Test health endpoint
curl -k https://your-domain.com/health

# Test API endpoint
curl -k https://your-domain.com/api/v1/status/health

# Test with authentication
curl -k -H "Authorization: Bearer YOUR_JWT_TOKEN" https://your-domain.com/api/v1/admin/system-info
```

### 12.2 Test MQTT Connection
```bash
# Test MQTT connection
mosquitto_pub -h localhost -p 1883 -u admin -P your_mqtt_password -t test/topic -m "Hello World"

# Subscribe to test
mosquitto_sub -h localhost -p 1883 -u admin -P your_mqtt_password -t test/topic
```

### 12.3 Monitor Logs
```bash
# Check API logs
tail -f /var/log/foodyeh/api.log

# Check MQTT logs
tail -f /var/log/mosquitto/mosquitto.log

# Check supervisor status
sudo supervisorctl status
```

## Step 13: Backup Strategy

### 13.1 Setup Automated Backups
```bash
# Create backup script
nano /home/foodyeh/backup.sh
```

Add backup script:
```bash
#!/bin/bash

# Backup database
pg_dump foodyeh_db > /home/foodyeh/backups/db_$(date +%Y%m%d_%H%M%S).sql

# Backup configuration files
tar -czf /home/foodyeh/backups/config_$(date +%Y%m%d_%H%M%S).tar.gz /home/foodyeh/foodyeh-backend/.env /etc/nginx/sites-available/foodyeh /etc/mosquitto/mosquitto.conf

# Keep only last 7 days of backups
find /home/foodyeh/backups -name "*.sql" -mtime +7 -delete
find /home/foodyeh/backups -name "*.tar.gz" -mtime +7 -delete
```

### 13.2 Setup Cron Job
```bash
# Add to crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/foodyeh/backup.sh
```

## Troubleshooting

### Common Issues

1. **API not accessible**
   - Check if uvicorn is running: `sudo supervisorctl status`
   - Check logs: `tail -f /var/log/foodyeh/api.log`
   - Check firewall: `sudo ufw status`

2. **MQTT connection issues**
   - Check Mosquitto status: `sudo systemctl status mosquitto`
   - Check MQTT logs: `tail -f /var/log/mosquitto/mosquitto.log`
   - Verify credentials in `/etc/mosquitto/passwd`

3. **SSL certificate issues**
   - Check certificate expiry: `sudo certbot certificates`
   - Renew manually: `sudo certbot renew`

4. **Database connection issues**
   - Check PostgreSQL status: `sudo systemctl status postgresql`
   - Test connection: `psql -h localhost -U foodyeh -d foodyeh_db`

## Security Checklist

- [ ] Firewall configured (UFW)
- [ ] SSL certificate installed
- [ ] HTTPS enforcement enabled
- [ ] JWT tokens configured
- [ ] MQTT authentication enabled
- [ ] Database secured
- [ ] Logs rotated
- [ ] Backups configured
- [ ] Monitoring in place

## Performance Optimization

1. **Database Optimization**
   - Enable connection pooling
   - Configure proper indexes
   - Regular VACUUM and ANALYZE

2. **API Optimization**
   - Enable response caching
   - Implement rate limiting
   - Use async operations

3. **System Optimization**
   - Configure swap if needed
   - Monitor resource usage
   - Optimize Nginx settings

## Maintenance

### Regular Tasks
- Monitor logs daily
- Check disk space weekly
- Update system monthly
- Renew SSL certificate (automatic)
- Test backups monthly

### Update Process
```bash
# Pull latest code
cd /home/foodyeh/foodyeh-backend
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Restart services
sudo supervisorctl restart foodyeh-api
sudo supervisorctl restart foodyeh-mqtt
```

This deployment guide ensures your FastAPI backend and MQTT server are properly configured for production use on Digital Ocean with security, monitoring, and maintenance considerations. 