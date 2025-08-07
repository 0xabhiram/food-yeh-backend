#!/bin/bash

# Digital Ocean Deployment Setup Script
# This script automates the initial setup of your Foodyeh backend server

set -e  # Exit on any error

echo "🚀 Starting Foodyeh Backend Deployment Setup..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root. Please run as a regular user with sudo privileges."
   exit 1
fi

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Python and system dependencies
print_status "Installing Python and system dependencies..."
sudo apt install python3.11 python3.11-pip python3.11-venv -y
sudo apt install nginx supervisor redis-server mosquitto mosquitto-clients -y
sudo apt install git curl wget unzip postgresql postgresql-contrib -y

# Install Fail2Ban for security
print_status "Installing Fail2Ban for security monitoring..."
sudo apt install fail2ban -y

# Install Node.js (for PM2 if needed)
print_status "Installing Node.js and PM2..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
sudo npm install -g pm2

# Create project directory
print_status "Setting up project directory..."
mkdir -p /home/$USER/foodyeh-backend
cd /home/$USER/foodyeh-backend

# Create virtual environment
print_status "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn[standard] python-multipart python-jose[cryptography] passlib[bcrypt] python-dotenv redis paho-mqtt sqlalchemy psycopg2-binary alembic structlog

# Create log directory
print_status "Setting up logging directory..."
sudo mkdir -p /var/log/foodyeh
sudo chown $USER:$USER /var/log/foodyeh

# Setup PostgreSQL
print_status "Setting up PostgreSQL database..."
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE foodyeh_db;"
sudo -u postgres psql -c "CREATE USER foodyeh WITH PASSWORD 'foodyeh_password_2024';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE foodyeh_db TO foodyeh;"
sudo -u postgres psql -c "ALTER USER foodyeh CREATEDB;"

# Configure Mosquitto MQTT
print_status "Configuring MQTT server..."
sudo tee /etc/mosquitto/mosquitto.conf > /dev/null <<EOF
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

# WebSocket support
listener 9001
protocol websockets
EOF

# Create MQTT password file
echo "foodyeh_mqtt_password" | sudo mosquitto_passwd -c /etc/mosquitto/passwd admin
sudo chown mosquitto:mosquitto /etc/mosquitto/passwd
sudo chmod 600 /etc/mosquitto/passwd

# Restart Mosquitto
sudo systemctl restart mosquitto
sudo systemctl enable mosquitto

# Create environment file
print_status "Creating environment configuration..."
cat > .env <<EOF
# Database Configuration
DATABASE_URL=postgresql://foodyeh:foodyeh_password_2024@localhost:5432/foodyeh_db

# JWT Configuration
SECRET_KEY=foodyeh_super_secret_key_2024_make_it_long_and_random_for_production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# MQTT Configuration
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=admin
MQTT_PASSWORD=foodyeh_mqtt_password

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
ADMIN_PASSWORD=admin_password_2024
ADMIN_EMAIL=admin@foodyeh.io
EOF

# Configure Nginx with enhanced security
print_status "Configuring Nginx with security headers..."
sudo tee /etc/nginx/sites-available/foodyeh > /dev/null <<EOF
# Enhanced Nginx configuration for Foodyeh API with security headers

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name api.foodyeh.io your-domain.com;
    
    # Security: Redirect all HTTP traffic to HTTPS
    return 301 https://\$host\$request_uri;
}

# HTTPS server configuration
server {
    listen 443 ssl http2;
    server_name api.foodyeh.io your-domain.com;
    
    # SSL Configuration (will be updated by certbot)
    ssl_certificate /etc/letsencrypt/live/api.foodyeh.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.foodyeh.io/privkey.pem;
    
    # SSL Security Settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets off;
    
    # Security Headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Permissions-Policy "geolocation=(), microphone=(), camera=(), payment=(), usb=(), magnetometer=(), gyroscope=(), accelerometer=()" always;
    
    # Disable autoindex for security
    autoindex off;
    
    # Hide server information
    server_tokens off;
    
    # API Proxy with security
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header X-Forwarded-Host \$host;
        proxy_set_header X-Forwarded-Port \$server_port;
        
        # Security: Prevent proxy caching of sensitive data
        proxy_cache_bypass \$http_authorization;
        proxy_no_cache \$http_authorization;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
        
        # Buffer settings
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
        
        # Security: Limit request body size
        client_max_body_size 10M;
        
        # CORS headers for API
        add_header Access-Control-Allow-Origin \$http_origin always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
        add_header Access-Control-Allow-Credentials true always;
        
        # Handle preflight requests
        if (\$request_method = 'OPTIONS') {
            add_header Access-Control-Allow-Origin \$http_origin;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With";
            add_header Access-Control-Allow-Credentials true;
            add_header Content-Type text/plain;
            add_header Content-Length 0;
            return 204;
        }
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000/health;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        # Security: No caching for health checks
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }
    
    # Root endpoint
    location / {
        proxy_pass http://127.0.0.1:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # Static files (if any)
    location /static/ {
        alias /home/$USER/foodyeh-backend/static/;
        expires 1y;
        add_header Cache-Control "public, immutable" always;
        add_header X-Content-Type-Options nosniff always;
        
        # Security: Prevent execution of uploaded files
        location ~* \.(php|pl|py|jsp|asp|sh|cgi)$ {
            deny all;
        }
    }
    
    # Security: Block access to sensitive files
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
    
    location ~* \.(htaccess|htpasswd|ini|log|sh|sql|conf)$ {
        deny all;
        access_log off;
        log_not_found off;
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
    
    # Security: Rate limiting (if not handled by FastAPI)
    limit_req_zone \$binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Logging for Fail2Ban
    access_log /var/log/nginx/foodyeh_access.log combined;
    error_log /var/log/nginx/foodyeh_error.log;
    
    # Security: Custom error pages
    error_page 404 /404.html;
    error_page 500 502 503 504 /50x.html;
    
    location = /404.html {
        root /usr/share/nginx/html;
        internal;
    }
    
    location = /50x.html {
        root /usr/share/nginx/html;
        internal;
    }
}

# Security: Additional server block for non-matching hosts
server {
    listen 80 default_server;
    listen 443 ssl default_server;
    server_name _;
    
    # Return 444 (connection closed without response)
    return 444;
}
EOF

# Enable Nginx site
sudo ln -sf /etc/nginx/sites-available/foodyeh /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
sudo systemctl enable nginx

# Configure Fail2Ban
print_status "Configuring Fail2Ban for API security..."
sudo tee /etc/fail2ban/jail.d/foodyeh-api.conf > /dev/null <<EOF
[foodyeh-api]
enabled = true
port = http,https
filter = foodyeh-api
logpath = /var/log/foodyeh/api.log
maxretry = 5
findtime = 600
bantime = 3600
ignoreip = 127.0.0.1 ::1
# Additional IPs to whitelist (add your admin IPs here)
# ignoreip = 127.0.0.1 ::1 192.168.1.100 10.0.0.50

# Ban action
banaction = ufw

# Log level
loglevel = info
EOF

# Create Fail2Ban filter
sudo tee /etc/fail2ban/filter.d/foodyeh-api.conf > /dev/null <<EOF
# Fail2Ban filter for Foodyeh API
# This filter parses structured JSON logs from the FastAPI application

[Definition]
# Filter name
failregex = ^.*"event":\s*"(unauthorized_access|auth_failure|https_violation|application_error)".*"ip":\s*"<HOST>".*$
            ^.*"level":\s*"warning".*"event":\s*"(unauthorized_access|auth_failure)".*"ip":\s*"<HOST>".*$
            ^.*"status":\s*(401|403|429).*"ip":\s*"<HOST>".*$

# Ignore regex (optional - for legitimate requests)
ignoreregex = ^.*"ip":\s*"<HOST>".*"status":\s*200.*$
              ^.*"ip":\s*"<HOST>".*"event":\s*"request_completed".*$

# Date format for the log
datepattern = ^.*"timestamp":\s*"([^"]+)".*$
EOF

# Restart Fail2Ban
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Configure Supervisor
print_status "Configuring Supervisor..."
sudo tee /etc/supervisor/conf.d/foodyeh.conf > /dev/null <<EOF
[program:foodyeh-api]
command=/home/$USER/foodyeh-backend/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
directory=/home/$USER/foodyeh-backend
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/foodyeh/api.log
environment=PYTHONPATH="/home/$USER/foodyeh-backend"

[program:foodyeh-mqtt]
command=/home/$USER/foodyeh-backend/venv/bin/python mqtt_client.py
directory=/home/$USER/foodyeh-backend
user=$USER
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/foodyeh/mqtt.log
environment=PYTHONPATH="/home/$USER/foodyeh-backend"
EOF

# Setup logrotate
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/foodyeh > /dev/null <<EOF
/var/log/foodyeh/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        supervisorctl restart foodyeh-api
        supervisorctl restart foodyeh-mqtt
        systemctl reload fail2ban
    endscript
}
EOF

# Configure firewall
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 1883
sudo ufw allow 9001

# Create backup script
print_status "Setting up backup script..."
mkdir -p /home/$USER/backups
cat > /home/$USER/backup.sh <<EOF
#!/bin/bash

# Backup database
pg_dump foodyeh_db > /home/$USER/backups/db_\$(date +%Y%m%d_%H%M%S).sql

# Backup configuration files
tar -czf /home/$USER/backups/config_\$(date +%Y%m%d_%H%M%S).tar.gz /home/$USER/foodyeh-backend/.env /etc/nginx/sites-available/foodyeh /etc/mosquitto/mosquitto.conf /etc/fail2ban/jail.d/foodyeh-api.conf

# Keep only last 7 days of backups
find /home/$USER/backups -name "*.sql" -mtime +7 -delete
find /home/$USER/backups -name "*.tar.gz" -mtime +7 -delete
EOF

chmod +x /home/$USER/backup.sh

# Add backup to crontab
(crontab -l 2>/dev/null; echo "0 2 * * * /home/$USER/backup.sh") | crontab -

# Install Certbot
print_status "Installing Certbot for SSL certificates..."
sudo apt install certbot python3-certbot-nginx -y

# Create a simple test file
print_status "Creating test files..."
mkdir -p /home/$USER/foodyeh-backend/static
echo "Foodyeh Backend is running!" > /home/$USER/foodyeh-backend/static/index.html

# Create a simple main.py for testing
cat > /home/$USER/foodyeh-backend/main.py <<EOF
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import os
from datetime import datetime

app = FastAPI(title="Foodyeh API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Trusted host middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # Configure properly for production
)

@app.get("/")
async def root():
    return {"message": "Foodyeh API is running!", "timestamp": datetime.now().isoformat()}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/api/v1/status/health")
async def api_health():
    return {
        "status": "healthy",
        "service": "foodyeh-api",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/status/mqtt")
async def mqtt_status():
    return {
        "status": "connected",
        "broker": "localhost:1883",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/admin/system-info")
async def system_info():
    return {
        "system": "Foodyeh Vending Machine",
        "version": "1.0.0",
        "uptime": "24h",
        "memory_usage": "45%",
        "disk_usage": "30%",
        "timestamp": datetime.now().isoformat()
    }
EOF

# Create a simple MQTT client
cat > /home/$USER/foodyeh-backend/mqtt_client.py <<EOF
import paho.mqtt.client as mqtt
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/foodyeh/mqtt_client.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# MQTT Configuration
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_USERNAME = "admin"
MQTT_PASSWORD = "foodyeh_mqtt_password"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info("Connected to MQTT broker successfully")
        # Subscribe to relevant topics
        client.subscribe("foodyeh/status")
        client.subscribe("foodyeh/orders")
        client.subscribe("foodyeh/health")
    else:
        logger.error(f"Failed to connect to MQTT broker with code: {rc}")

def on_message(client, userdata, msg):
    logger.info(f"Received message on topic {msg.topic}: {msg.payload.decode()}")

def on_disconnect(client, userdata, rc):
    logger.info("Disconnected from MQTT broker")

def main():
    client = mqtt.Client()
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        # Keep the client running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Stopping MQTT client...")
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        logger.error(f"Error in MQTT client: {e}")

if __name__ == "__main__":
    main()
EOF

# Reload supervisor
print_status "Starting services..."
sudo supervisorctl reread
sudo supervisorctl update

# Final status check
print_status "Performing final status checks..."

# Check if services are running
if sudo systemctl is-active --quiet nginx; then
    print_status "✅ Nginx is running"
else
    print_warning "⚠️  Nginx is not running"
fi

if sudo systemctl is-active --quiet postgresql; then
    print_status "✅ PostgreSQL is running"
else
    print_warning "⚠️  PostgreSQL is not running"
fi

if sudo systemctl is-active --quiet mosquitto; then
    print_status "✅ Mosquitto MQTT is running"
else
    print_warning "⚠️  Mosquitto MQTT is not running"
fi

if sudo systemctl is-active --quiet redis-server; then
    print_status "✅ Redis is running"
else
    print_warning "⚠️  Redis is not running"
fi

if sudo systemctl is-active --quiet fail2ban; then
    print_status "✅ Fail2Ban is running"
else
    print_warning "⚠️  Fail2Ban is not running"
fi

# Check supervisor status
print_status "Checking supervisor services..."
sudo supervisorctl status

# Check Fail2Ban status
print_status "Checking Fail2Ban status..."
sudo fail2ban-client status

print_status "🎉 Setup completed successfully!"
print_status ""
print_status "📋 Next steps:"
print_status "1. Update your domain name in Nginx configuration"
print_status "2. Get SSL certificate: sudo certbot --nginx -d your-domain.com"
print_status "3. Update .env file with your actual domain"
print_status "4. Upload your FastAPI backend code to /home/$USER/foodyeh-backend/"
print_status "5. Restart services: sudo supervisorctl restart foodyeh-api"
print_status "6. Monitor Fail2Ban: sudo fail2ban-client status foodyeh-api"
print_status ""
print_status "📁 Important files:"
print_status "- Environment: /home/$USER/foodyeh-backend/.env"
print_status "- Nginx config: /etc/nginx/sites-available/foodyeh"
print_status "- Supervisor config: /etc/supervisor/conf.d/foodyeh.conf"
print_status "- Fail2Ban config: /etc/fail2ban/jail.d/foodyeh-api.conf"
print_status "- Logs: /var/log/foodyeh/"
print_status ""
print_status "🔧 Useful commands:"
print_status "- Check logs: tail -f /var/log/foodyeh/api.log"
print_status "- Restart API: sudo supervisorctl restart foodyeh-api"
print_status "- Check status: sudo supervisorctl status"
print_status "- Test API: curl http://localhost:8000/health"
print_status "- Monitor Fail2Ban: sudo fail2ban-client status"
print_status "- View banned IPs: sudo fail2ban-client banned" 