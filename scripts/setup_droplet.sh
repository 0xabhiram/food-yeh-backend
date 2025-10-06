#!/bin/bash

# Foodyeh Droplet Setup Script
# Run this script on your Ubuntu droplet to set up the backend

set -e  # Exit on any error

echo "🍔 Setting up Foodyeh Backend on Ubuntu Droplet..."

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

# Update system
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install system dependencies
print_status "Installing system dependencies..."
sudo apt install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-venv \
    rustc \
    cargo \
    pkg-config \
    libssl-dev \
    libffi-dev \
    curl \
    git \
    nginx \
    redis-server \
    mosquitto \
    mosquitto-clients \
    fail2ban \
    ufw \
    certbot \
    python3-certbot-nginx \
    logrotate

# Install Python 3.11 (more stable for pydantic)
print_status "Installing Python 3.11..."
sudo apt install -y python3.11 python3.11-dev python3.11-venv python3.11-pip

# Create application directory
print_status "Creating application directory..."
sudo mkdir -p /opt/foodyeh
sudo chown $USER:$USER /opt/foodyeh

# Clone or copy your project
print_status "Setting up project files..."
cd /opt/foodyeh

# If you have the project files, copy them here
# Otherwise, you can clone from your repository
# git clone https://github.com/yourusername/foodyeh-poc-1.git .

# Create virtual environment with Python 3.11
print_status "Creating Python virtual environment..."
python3.11 -m venv venv
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
cd backend

# Try installing with pre-compiled wheels first
print_status "Installing pydantic with pre-compiled wheels..."
pip install --only-binary=all pydantic==2.4.2 pydantic-settings==2.0.3

# Install remaining requirements
print_status "Installing remaining requirements..."
pip install -r requirements.txt

# Create .env file
print_status "Creating environment configuration..."
if [ ! -f .env ]; then
    cat > .env << EOF
# Foodyeh API Environment Configuration
API_BASE=https://api.foodyeh.io
DEBUG=false
ENVIRONMENT=production
DB_URL=sqlite+aiosqlite:///./foodyeh.db
JWT_SECRET=your-super-secret-jwt-key-64-characters-minimum-required-for-hs512
JWT_ALGO=HS512
ACCESS_TTL_MIN=15
REFRESH_TTL_DAYS=7
REDIS_URL=redis://127.0.0.1:6379/0
CORS_ORIGINS=["https://api.foodyeh.io","https://app.foodyeh.io","https://foodyeh.io"]
MQTT_HOST=api.foodyeh.io
MQTT_PORT=443
MQTT_USE_WEBSOCKETS=true
MQTT_WS_PATH=/mqtt
MQTT_USE_TLS=true
MQTT_USERNAME=backend
MQTT_PASSWORD=your-strong-mqtt-password-here
RATE_LIMIT_AUTH=5
RATE_LIMIT_API=300
RATE_LIMIT_WINDOW=600
ACCOUNT_LOCKOUT_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=600
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=["jpg","jpeg","png","gif","webp"]
UPLOAD_DIR=./uploads
BCRYPT_ROUNDS=12
MIN_PASSWORD_LENGTH=8
REQUIRE_SPECIAL_CHAR=true
REQUIRE_UPPERCASE=true
REQUIRE_LOWERCASE=true
REQUIRE_NUMBER=true
LOG_LEVEL=INFO
LOG_FILE=/var/log/foodyeh/api.log
ADMIN_EMAIL=admin@foodyeh.io
ADMIN_PASSWORD=ChangeThisPassword123!
ADMIN_FIRST_NAME=Admin
ADMIN_LAST_NAME=User
EOF
    print_warning "Created .env file. Please update the JWT_SECRET and other sensitive values!"
fi

# Initialize database
print_status "Initializing database..."
python seed_data.py

# Create log directory
print_status "Creating log directory..."
sudo mkdir -p /var/log/foodyeh
sudo chown $USER:$USER /var/log/foodyeh

# Create uploads directory
print_status "Creating uploads directory..."
mkdir -p uploads

# Set up systemd service
print_status "Setting up systemd service..."
sudo tee /etc/systemd/system/foodyeh-api.service > /dev/null << EOF
[Unit]
Description=Foodyeh API Service
After=network.target
Wants=network.target

[Service]
Type=exec
User=$USER
Group=$USER
WorkingDirectory=/opt/foodyeh/backend
EnvironmentFile=/opt/foodyeh/backend/.env
ExecStart=/opt/foodyeh/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal
SyslogIdentifier=foodyeh-api

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/foodyeh/backend /var/log/foodyeh
ProtectKernelTunables=true
ProtectKernelModules=true
ProtectControlGroups=true
RestrictRealtime=true
RestrictSUIDSGID=true

# Resource limits
LimitNOFILE=65536
LimitNPROC=4096

[Install]
WantedBy=multi-user.target
EOF

# Enable and start services
print_status "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable foodyeh-api
sudo systemctl enable redis-server
sudo systemctl enable mosquitto

# Start services
sudo systemctl start redis-server
sudo systemctl start mosquitto
sudo systemctl start foodyeh-api

# Configure firewall
print_status "Configuring firewall..."
sudo ufw --force enable
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw deny 1883/tcp
sudo ufw deny 9001/tcp

# Configure Nginx (basic setup)
print_status "Setting up Nginx..."
sudo tee /etc/nginx/sites-available/foodyeh-api > /dev/null << EOF
server {
    listen 80;
    server_name api.foodyeh.io;

    # Rate limiting
    limit_req_zone \$binary_remote_addr zone=auth:10m rate=5r/m;
    limit_req_zone \$binary_remote_addr zone=api:10m rate=300r/m;
    limit_conn_zone \$binary_remote_addr zone=api_conn:10m;

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header Referrer-Policy "strict-origin-when-cross-origin";
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';";

    # API proxy
    location / {
        limit_req zone=api burst=50 nodelay;
        limit_conn api_conn 10;
        
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # MQTT WebSocket proxy
    location /mqtt {
        proxy_pass http://127.0.0.1:9001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_read_timeout 86400;
    }

    # Auth endpoints with stricter rate limiting
    location /auth/ {
        limit_req zone=auth burst=10 nodelay;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

# Enable site
sudo ln -sf /etc/nginx/sites-available/foodyeh-api /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# Configure Mosquitto
print_status "Configuring Mosquitto..."
sudo tee /etc/mosquitto/conf.d/foodyeh.conf > /dev/null << EOF
# Foodyeh MQTT Configuration
listener 1883 127.0.0.1
protocol mqtt

listener 9001 127.0.0.1
protocol websockets

allow_anonymous false
password_file /etc/mosquitto/passwd

log_type all
log_dest file /var/log/mosquitto/mosquitto.log
log_dest stdout

max_connections 100
max_inflight_messages 20
max_queued_messages 100

persistence true
persistence_location /var/lib/mosquitto/
EOF

# Create MQTT users
print_status "Setting up MQTT users..."
sudo mosquitto_passwd -c /etc/mosquitto/passwd backend
sudo mosquitto_passwd -b /etc/mosquitto/passwd foodyeh_device your_device_password
sudo chown mosquitto:mosquitto /etc/mosquitto/passwd
sudo chmod 600 /etc/mosquitto/passwd

# Restart Mosquitto
sudo systemctl restart mosquitto

# Set up log rotation
print_status "Setting up log rotation..."
sudo tee /etc/logrotate.d/foodyeh-api > /dev/null << EOF
/var/log/foodyeh/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
    postrotate
        systemctl reload foodyeh-api > /dev/null 2>&1 || true
    endscript
}

/var/log/mosquitto/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 644 mosquitto mosquitto
    postrotate
        systemctl reload mosquitto > /dev/null 2>&1 || true
    endscript
}
EOF

# Configure Fail2ban
print_status "Setting up Fail2ban..."
sudo tee /etc/fail2ban/jail.local > /dev/null << EOF
[nginx-limit-req]
enabled = true
port = http,https
filter = nginx-limit-req
logpath = /var/log/nginx/error.log
maxretry = 10
bantime = 3600
findtime = 600

[nginx-http-auth]
enabled = true
port = http,https
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 1800
findtime = 300

[foodyeh-auth]
enabled = true
port = http,https
filter = foodyeh-auth
logpath = /var/log/foodyeh/api.log
maxretry = 10
bantime = 7200
findtime = 600
EOF

sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Health check
print_status "Performing health check..."
sleep 5

if systemctl is-active --quiet foodyeh-api; then
    print_status "✅ Foodyeh API service is running"
else
    print_error "❌ Foodyeh API service failed to start"
    sudo systemctl status foodyeh-api
fi

if systemctl is-active --quiet nginx; then
    print_status "✅ Nginx is running"
else
    print_error "❌ Nginx failed to start"
fi

if systemctl is-active --quiet redis-server; then
    print_status "✅ Redis is running"
else
    print_error "❌ Redis failed to start"
fi

if systemctl is-active --quiet mosquitto; then
    print_status "✅ Mosquitto is running"
else
    print_error "❌ Mosquitto failed to start"
fi

# Final instructions
echo ""
echo "🎉 Foodyeh Backend Setup Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Update your domain DNS to point to this server"
echo "2. Get SSL certificate: sudo certbot --nginx -d api.foodyeh.io"
echo "3. Update .env file with your actual secrets"
echo "4. Test the API: curl http://localhost:8000/health"
echo ""
echo "🔧 Useful Commands:"
echo "- Check API status: sudo systemctl status foodyeh-api"
echo "- View API logs: sudo journalctl -u foodyeh-api -f"
echo "- Check Nginx: sudo nginx -t"
echo "- View firewall status: sudo ufw status"
echo ""
echo "🌐 Your API will be available at: http://api.foodyeh.io"
echo "📊 API Documentation: http://api.foodyeh.io/docs"
echo ""
