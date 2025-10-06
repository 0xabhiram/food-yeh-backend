# 🍔 Foodyeh - Smart Vending Machine Management System

[![Flutter](https://img.shields.io/badge/Flutter-02569B?style=for-the-badge&logo=flutter&logoColor=white)](https://flutter.dev/)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Dart](https://img.shields.io/badge/Dart-0175C2?style=for-the-badge&logo=dart&logoColor=white)](https://dart.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

A comprehensive smart vending machine management system featuring a Flutter mobile app with FastAPI backend, real-time MQTT communication, secure authentication, and admin dashboard.

## 📋 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [File Explanations](#-file-explanations)
- [Prerequisites](#-prerequisites)
- [Local Development](#-local-development)
- [Cloud Deployment](#-cloud-deployment)
  - [AWS Deployment](#aws-deployment)
  - [Google Cloud Platform (GCP)](#google-cloud-platform-gcp)
  - [DigitalOcean](#digitalocean)
  - [Azure](#azure)
- [Configuration](#-configuration)
- [API Documentation](#-api-documentation)
- [Security Features](#-security-features)
- [Monitoring & Logging](#-monitoring--logging)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Features

### Frontend (Flutter)
- **Cross-platform mobile app** (Android, iOS, Web, Windows)
- **Modern UI/UX** with Material Design 3 and dark theme
- **Real-time updates** via MQTT WebSocket connection
- **Secure authentication** with JWT tokens and refresh mechanism
- **Role-based access control** (Admin/User roles)
- **Order management** with status tracking
- **Shopping cart** with persistent storage
- **Profile management** and user settings
- **Admin dashboard** for system management

### Backend (FastAPI)
- **RESTful API** with automatic OpenAPI documentation
- **JWT authentication** with secure token handling
- **Role-based access control** (RBAC) system
- **MQTT integration** for real-time communication
- **SQLite database** (easily swappable to PostgreSQL/MySQL)
- **File upload handling** with security validation
- **Rate limiting** and brute force protection
- **OWASP Top-10 security** compliance
- **Comprehensive logging** and monitoring
- **CORS protection** with configurable origins

### DevOps & Infrastructure
- **Production-ready deployment** configurations
- **Nginx reverse proxy** with SSL/TLS termination
- **Docker containerization** support
- **Fail2ban intrusion prevention**
- **Automated backups** and log rotation
- **Health checks** and monitoring endpoints
- **Systemd service** management

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flutter App   │    │   FastAPI       │    │   Database      │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (SQLite/      │
│                 │    │                 │    │    PostgreSQL)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MQTT Client   │    │   MQTT Broker   │    │   File Storage  │
│   (Real-time)   │◄──►│   (Mosquitto)   │    │   (Uploads)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
foodyeh-poc-1/
├── 📱 frontend/                    # Flutter mobile application
│   ├── lib/
│   │   ├── core/                   # Core utilities and constants
│   │   │   ├── constants/
│   │   │   │   └── app_constants.dart
│   │   │   └── theme/
│   │   │       └── app_theme.dart
│   │   ├── models/                 # Data models and DTOs
│   │   │   ├── create_order_request.dart
│   │   │   ├── dish.dart
│   │   │   ├── order.dart
│   │   │   ├── requests.dart
│   │   │   ├── signup_request.dart
│   │   │   └── user.dart
│   │   ├── provider/               # State management (Provider pattern)
│   │   │   ├── auth_provider.dart
│   │   │   └── cart_provider.dart
│   │   ├── screens/                # UI screens and pages
│   │   │   ├── admin_analytics_screen.dart
│   │   │   ├── admin_dashboard_screen.dart
│   │   │   ├── admin_dish_management_screen.dart
│   │   │   ├── admin_order_management_screen.dart
│   │   │   ├── admin_user_management_screen.dart
│   │   │   ├── cart_screen.dart
│   │   │   ├── home_screen.dart
│   │   │   ├── login_screen.dart
│   │   │   ├── order_status_screen.dart
│   │   │   └── profile_screen.dart
│   │   ├── services/               # API services and HTTP client
│   │   │   └── api_service.dart
│   │   ├── widgets/                # Reusable UI components
│   │   │   ├── custom_button.dart
│   │   │   └── custom_text_field.dart
│   │   └── main.dart               # Application entry point
│   ├── assets/                     # Static assets
│   │   └── images/
│   │       └── foodyeh_logo.png
│   ├── android/                    # Android-specific configurations
│   ├── ios/                        # iOS-specific configurations
│   ├── web/                        # Web-specific configurations
│   ├── windows/                    # Windows-specific configurations
│   ├── linux/                      # Linux-specific configurations
│   ├── macos/                      # macOS-specific configurations
│   └── pubspec.yaml                # Flutter dependencies and metadata
├── 🐍 backend/                     # FastAPI Python backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # FastAPI application entry point
│   │   ├── config.py               # Application configuration
│   │   ├── database.py             # Database connection and setup
│   │   ├── logging_config.py       # Logging configuration
│   │   ├── auth.py                 # Authentication utilities
│   │   ├── models.py               # SQLAlchemy database models
│   │   ├── schemas.py              # Pydantic request/response schemas
│   │   ├── middleware/             # Custom middleware
│   │   │   └── auth_middleware.py  # JWT authentication middleware
│   │   ├── routers/                # API route handlers
│   │   │   ├── admin.py            # Admin-specific endpoints
│   │   │   ├── auth.py             # Authentication endpoints
│   │   │   ├── dishes.py           # Dish management endpoints
│   │   │   └── orders.py           # Order management endpoints
│   │   ├── services/               # Business logic services
│   │   │   └── mqtt_client.py      # MQTT client service
│   │   └── utils/                  # Utility functions
│   │       ├── rate_limiter.py     # Rate limiting utilities
│   │       └── security.py         # Security utilities
│   ├── requirements.txt            # Python dependencies
│   ├── check_admin_user.py         # Admin user verification script
│   ├── check_database.py           # Database health check script
│   ├── fix_admin_role.py           # Admin role setup script
│   ├── run_simple.py               # Simple server runner
│   └── setup_sqlite.py             # SQLite database setup
├── 🌐 nginx/                       # Nginx configuration files
├── ⚙️ systemd/                     # Systemd service files
├── 📨 mosquitto/                   # MQTT broker configuration
├── 🔄 logrotate/                   # Log rotation configuration
├── 🛡️ fail2ban/                    # Intrusion prevention configuration
├── 📜 scripts/                     # Deployment and utility scripts
│   ├── setup_droplet.sh            # DigitalOcean droplet setup
│   └── backup.sh                   # Backup script
├── 📄 mosquitto.conf               # MQTT broker configuration
├── 🐳 docker-compose.dev.yml       # Docker development setup
├── 📝 .gitignore                   # Git ignore rules
└── 📖 README.md                    # This file
```

## 📄 File Explanations

### Frontend Files

#### Core Files
- **`main.dart`**: Application entry point, initializes providers and routing
- **`app_constants.dart`**: Application-wide constants (API URLs, timeouts, etc.)
- **`app_theme.dart`**: Material Design 3 theme configuration with dark mode

#### Models
- **`user.dart`**: User model with authentication fields
- **`dish.dart`**: Food item model with pricing and availability
- **`order.dart`**: Order model with status tracking
- **`create_order_request.dart`**: Order creation request DTO
- **`signup_request.dart`**: User registration request DTO

#### Providers (State Management)
- **`auth_provider.dart`**: Authentication state management (login, logout, token refresh)
- **`cart_provider.dart`**: Shopping cart state management

#### Screens
- **`login_screen.dart`**: User authentication screen
- **`home_screen.dart`**: Main dish browsing screen with 3x3 grid
- **`cart_screen.dart`**: Shopping cart management
- **`profile_screen.dart`**: User profile and settings
- **`order_status_screen.dart`**: Order tracking and status
- **`admin_dashboard_screen.dart`**: Admin overview with statistics
- **`admin_dish_management_screen.dart`**: CRUD operations for dishes
- **`admin_user_management_screen.dart`**: User management interface
- **`admin_order_management_screen.dart`**: Order management interface
- **`admin_analytics_screen.dart`**: Analytics and reporting

#### Services
- **`api_service.dart`**: HTTP client for backend communication with error handling

#### Widgets
- **`custom_button.dart`**: Reusable button component
- **`custom_text_field.dart`**: Reusable text input component

### Backend Files

#### Core Application
- **`main.py`**: FastAPI application initialization, middleware setup, route registration
- **`config.py`**: Environment-based configuration management
- **`database.py`**: Database connection, session management, and initialization
- **`logging_config.py`**: Structured logging configuration with different levels
- **`auth.py`**: JWT token generation, validation, and password hashing utilities

#### Models & Schemas
- **`models.py`**: SQLAlchemy ORM models for database tables
- **`schemas.py`**: Pydantic models for request/response validation

#### Middleware
- **`auth_middleware.py`**: Global JWT authentication middleware with role-based access

#### Routers (API Endpoints)
- **`auth.py`**: Authentication endpoints (login, signup, token refresh)
- **`dishes.py`**: Dish management endpoints (CRUD operations)
- **`orders.py`**: Order management endpoints (create, update, track)
- **`admin.py`**: Admin-specific endpoints (user management, analytics)

#### Services
- **`mqtt_client.py`**: MQTT broker connection and message handling

#### Utilities
- **`rate_limiter.py`**: Rate limiting implementation for API protection
- **`security.py`**: Security utilities (password validation, input sanitization)

#### Helper Scripts
- **`check_admin_user.py`**: Verify admin user existence and permissions
- **`check_database.py`**: Database connectivity and health checks
- **`fix_admin_role.py`**: Set up admin user roles and permissions
- **`run_simple.py`**: Simple development server runner
- **`setup_sqlite.py`**: SQLite database initialization and schema creation

### Infrastructure Files

#### Nginx Configuration
- **`nginx/`**: Production-ready Nginx configuration with SSL, security headers, and reverse proxy

#### Systemd Services
- **`systemd/`**: Service files for running the application as a system service

#### MQTT Configuration
- **`mosquitto.conf`**: MQTT broker configuration with authentication and security
- **`mosquitto/`**: Additional MQTT broker configuration files

#### Log Management
- **`logrotate/`**: Log rotation configuration to prevent disk space issues

#### Security
- **`fail2ban/`**: Intrusion prevention system configuration

#### Scripts
- **`setup_droplet.sh`**: Automated DigitalOcean droplet setup script
- **`backup.sh`**: Database and file backup automation

## 🔧 Prerequisites

### Development Environment
- **Flutter SDK** 3.8.0 or higher
- **Python** 3.10 or higher
- **Git** for version control
- **Android Studio** (for mobile development)
- **VS Code** or **IntelliJ IDEA** (recommended IDEs)

### System Dependencies (Linux/macOS)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y build-essential python3-dev rustc cargo pkg-config libssl-dev libffi-dev

# macOS
brew install python@3.10 rust pkg-config openssl
```

### Database Options
- **SQLite** (default, included)
- **PostgreSQL** (recommended for production)
- **MySQL** (alternative option)

## 🚀 Local Development

### 1. Clone the Repository
```bash
git clone https://github.com/0xabhiram/food-yeh-backend.git
cd food-yeh-backend
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows Command Prompt:
venv\Scripts\activate.bat
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
cp env_example.txt .env
# Edit .env with your configuration

# Initialize database
python setup_sqlite.py

# Run development server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Install Flutter dependencies
flutter pub get

# Run the application
flutter run
```

### 4. MQTT Setup (Optional)
```bash
# Install Mosquitto MQTT broker
# Ubuntu/Debian:
sudo apt-get install mosquitto mosquitto-clients

# macOS:
brew install mosquitto

# Start MQTT broker
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

## ☁️ Cloud Deployment

### AWS Deployment

#### Option 1: AWS Lightsail (Simplest)
```bash
# 1. Create Lightsail instance
# - Go to AWS Lightsail Console
# - Create instance: Ubuntu 22.04 LTS
# - Choose appropriate plan (1GB RAM minimum)
# - Create static IP and attach to instance

# 2. Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# 3. Install dependencies
sudo apt update
sudo apt install -y python3-pip python3-venv nginx git

# 4. Clone and setup application
cd /opt
sudo git clone https://github.com/0xabhiram/food-yeh-backend.git foodyeh
sudo chown -R ubuntu:ubuntu foodyeh
cd foodyeh

# 5. Setup Python environment
cd backend
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 6. Configure environment
cat > .env << 'EOF'
ENV=production
SECRET_KEY=your-super-secret-jwt-key-64-characters-minimum
CORS_ORIGINS=*
DATABASE_URL=sqlite+aiosqlite:///./foodyeh.db
EOF

# 7. Initialize database
python setup_sqlite.py

# 8. Create systemd service
sudo tee /etc/systemd/system/foodyeh.service >/dev/null <<'EOF'
[Unit]
Description=Foodyeh FastAPI Service
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/opt/foodyeh/backend
EnvironmentFile=/opt/foodyeh/backend/.env
ExecStart=/opt/foodyeh/backend/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 9. Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable foodyeh
sudo systemctl start foodyeh

# 10. Configure Nginx
sudo tee /etc/nginx/sites-available/foodyeh >/dev/null <<'EOF'
server {
    listen 80;
    server_name _;
    client_max_body_size 25m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -s /etc/nginx/sites-available/foodyeh /etc/nginx/sites-enabled/foodyeh
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 11. Setup SSL with Let's Encrypt
sudo apt install -y certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com --non-interactive --agree-tos -m your-email@example.com
```

#### Option 2: AWS EC2 + RDS
```bash
# 1. Launch EC2 instance (Ubuntu 22.04)
# 2. Create RDS PostgreSQL instance
# 3. Configure security groups (allow 80, 443, 22, 5432)
# 4. Follow similar setup as Lightsail but use RDS connection string

# Environment variables for RDS:
DATABASE_URL=postgresql://username:password@your-rds-endpoint:5432/foodyeh
```

#### Option 3: AWS Elastic Beanstalk
```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize EB application
eb init foodyeh-backend

# 3. Create environment
eb create production

# 4. Set environment variables in EB console
# 5. Deploy
eb deploy
```

### Google Cloud Platform (GCP)

#### Option 1: Compute Engine
```bash
# 1. Create VM instance
gcloud compute instances create foodyeh-backend \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --zone=us-central1-a

# 2. Setup firewall rules
gcloud compute firewall-rules create allow-http-https \
    --allow tcp:80,tcp:443,tcp:22

# 3. Connect and setup (similar to AWS Lightsail)
gcloud compute ssh foodyeh-backend --zone=us-central1-a
```

#### Option 2: Cloud Run (Containerized)
```bash
# 1. Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.10-slim

WORKDIR /app
COPY backend/requirements.txt .
RUN pip install -r requirements.txt

COPY backend/ .
EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# 2. Build and deploy
gcloud builds submit --tag gcr.io/your-project/foodyeh-backend
gcloud run deploy foodyeh-backend \
    --image gcr.io/your-project/foodyeh-backend \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

#### Option 3: App Engine
```bash
# 1. Create app.yaml
cat > app.yaml << 'EOF'
runtime: python310
service: foodyeh-backend

env_variables:
  ENV: production
  SECRET_KEY: your-secret-key
  CORS_ORIGINS: "*"

automatic_scaling:
  min_instances: 1
  max_instances: 10
EOF

# 2. Deploy
gcloud app deploy
```

### DigitalOcean

#### Droplet Setup
```bash
# 1. Create droplet (Ubuntu 22.04, 1GB RAM minimum)
# 2. Use the provided setup script
chmod +x scripts/setup_droplet.sh
./scripts/setup_droplet.sh

# 3. Manual setup (alternative)
# Follow similar steps as AWS Lightsail
```

#### App Platform
```bash
# 1. Create app.yaml for App Platform
cat > .do/app.yaml << 'EOF'
name: foodyeh-backend
services:
- name: api
  source_dir: backend
  github:
    repo: 0xabhiram/food-yeh-backend
    branch: main
  run_command: uvicorn app.main:app --host 0.0.0.0 --port 8080
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  envs:
  - key: ENV
    value: production
  - key: SECRET_KEY
    value: your-secret-key
  - key: CORS_ORIGINS
    value: "*"
  http_port: 8080
  routes:
  - path: /
EOF
```

### Azure

#### Virtual Machine
```bash
# 1. Create VM using Azure CLI
az vm create \
    --resource-group foodyeh-rg \
    --name foodyeh-backend \
    --image Ubuntu2204 \
    --size Standard_B1s \
    --admin-username azureuser \
    --generate-ssh-keys

# 2. Open ports
az vm open-port --port 80 --resource-group foodyeh-rg --name foodyeh-backend
az vm open-port --port 443 --resource-group foodyeh-rg --name foodyeh-backend

# 3. Connect and setup
ssh azureuser@your-vm-ip
# Follow similar setup as other cloud providers
```

#### Container Instances
```bash
# 1. Create container instance
az container create \
    --resource-group foodyeh-rg \
    --name foodyeh-backend \
    --image your-registry/foodyeh-backend \
    --ports 8000 \
    --environment-variables \
        ENV=production \
        SECRET_KEY=your-secret-key \
        CORS_ORIGINS="*"
```

## ⚙️ Configuration

### Environment Variables

#### Backend Configuration
```bash
# Application Settings
ENV=production                    # Environment (development/production)
DEBUG=false                       # Debug mode
API_BASE=https://api.foodyeh.io   # API base URL

# Database Configuration
DATABASE_URL=sqlite+aiosqlite:///./foodyeh.db  # SQLite (default)
# DATABASE_URL=postgresql://user:pass@host:5432/dbname  # PostgreSQL
# DATABASE_URL=mysql+pymysql://user:pass@host:3306/dbname  # MySQL

# JWT Authentication
JWT_SECRET=your-super-secret-jwt-key-64-characters-minimum
JWT_ALGORITHM=HS512
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS Configuration
CORS_ORIGINS=*                    # Allow all origins (development)
# CORS_ORIGINS=https://yourdomain.com,https://app.yourdomain.com  # Production

# MQTT Configuration (Optional)
MQTT_HOST=localhost
MQTT_PORT=1883
MQTT_USERNAME=
MQTT_PASSWORD=
MQTT_USE_WEBSOCKETS=false
MQTT_USE_TLS=false

# Security Settings
RATE_LIMIT_AUTH=5                 # Login attempts per minute
RATE_LIMIT_API=300                # API requests per minute
ACCOUNT_LOCKOUT_ATTEMPTS=5        # Failed attempts before lockout
ACCOUNT_LOCKOUT_DURATION=600      # Lockout duration in seconds

# File Upload Settings
MAX_FILE_SIZE=10485760            # 10MB in bytes
ALLOWED_FILE_TYPES=image/jpeg,image/png,image/gif

# Logging
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=/var/log/foodyeh/app.log
```

#### Frontend Configuration
```dart
// lib/core/constants/app_constants.dart
class AppConstants {
  static const String apiBaseUrl = 'https://api.foodyeh.io';
  static const String mqttHost = 'api.foodyeh.io';
  static const int mqttPort = 443;
  static const bool mqttUseWebSockets = true;
  static const String mqttWebSocketPath = '/mqtt';
  static const bool mqttUseTLS = true;
}
```

## 📚 API Documentation

### Base URL
- **Development**: `http://localhost:8000`
- **Production**: `https://api.foodyeh.io`

### Interactive Documentation
- **Swagger UI**: `{base_url}/docs`
- **ReDoc**: `{base_url}/redoc`

### Authentication Endpoints
```http
POST /auth/login
POST /auth/signup
POST /auth/refresh
POST /auth/logout
GET /auth/me
```

### Dish Management
```http
GET /dishes/              # Get all dishes
GET /dishes/{id}          # Get dish by ID
POST /dishes/             # Create dish (Admin only)
PUT /dishes/{id}          # Update dish (Admin only)
DELETE /dishes/{id}       # Delete dish (Admin only)
```

### Order Management
```http
GET /orders/              # Get user orders
POST /orders/             # Create new order
GET /orders/{id}          # Get order details
PUT /orders/{id}/status   # Update order status (Admin only)
```

### Admin Endpoints
```http
GET /admin/users/         # Get all users (Admin only)
GET /admin/analytics/     # Get analytics data (Admin only)
GET /admin/health/        # System health check
```

## 🔒 Security Features

### Authentication & Authorization
- **JWT-based authentication** with secure token handling
- **Refresh token mechanism** for seamless user experience
- **Role-based access control** (Admin/User roles)
- **Password hashing** using bcrypt with salt rounds

### API Security
- **Rate limiting** to prevent brute force attacks
- **CORS protection** with configurable origins
- **Input validation** and sanitization using Pydantic
- **SQL injection prevention** with parameterized queries
- **XSS protection** with content security policies

### Infrastructure Security
- **HTTPS/TLS encryption** for all communications
- **Security headers** (HSTS, CSP, X-Frame-Options)
- **Fail2ban integration** for intrusion prevention
- **File upload security** with type and size validation
- **Account lockout** after failed login attempts

### Data Protection
- **Environment variable** management for secrets
- **Database connection encryption** (when using PostgreSQL/MySQL)
- **Secure file storage** with access controls
- **Log sanitization** to prevent sensitive data exposure

## 📊 Monitoring & Logging

### Application Logs
```bash
# View application logs
journalctl -u foodyeh -f

# View specific log levels
journalctl -u foodyeh --since "1 hour ago" --priority=err

# Log file location
tail -f /var/log/foodyeh/app.log
```

### Nginx Logs
```bash
# Access logs
tail -f /var/log/nginx/access.log

# Error logs
tail -f /var/log/nginx/error.log
```

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database connectivity
python backend/check_database.py

# Admin user verification
python backend/check_admin_user.py
```

### Monitoring Setup
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# System resource monitoring
htop
iotop
nethogs

# Disk usage monitoring
df -h
du -sh /var/log/foodyeh/
```

## 🐛 Troubleshooting

### Common Issues

#### Backend Won't Start
```bash
# Check Python version
python3 --version

# Check virtual environment
which python
pip list

# Check port availability
sudo netstat -tlnp | grep :8000

# Check logs
journalctl -u foodyeh --no-pager
```

#### Database Connection Issues
```bash
# Check database file permissions
ls -la backend/foodyeh.db

# Test database connection
python backend/check_database.py

# Recreate database
rm backend/foodyeh.db
python backend/setup_sqlite.py
```

#### Frontend Build Issues
```bash
# Clean Flutter cache
flutter clean
flutter pub get

# Check Flutter version
flutter --version

# Check dependencies
flutter pub deps
```

#### MQTT Connection Issues
```bash
# Check MQTT broker status
sudo systemctl status mosquitto

# Test MQTT connection
mosquitto_pub -h localhost -t test -m "hello"
mosquitto_sub -h localhost -t test

# Check MQTT logs
sudo journalctl -u mosquitto -f
```

#### Nginx Configuration Issues
```bash
# Test nginx configuration
sudo nginx -t

# Check nginx status
sudo systemctl status nginx

# Reload nginx
sudo systemctl reload nginx
```

### Performance Optimization

#### Backend Optimization
```bash
# Increase worker processes
# Edit systemd service file
ExecStart=/opt/foodyeh/backend/venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --workers 4

# Enable gzip compression in nginx
gzip on;
gzip_types text/plain application/json application/javascript text/css;
```

#### Database Optimization
```bash
# For PostgreSQL, add indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_created_at ON orders(created_at);

# For SQLite, enable WAL mode
PRAGMA journal_mode=WAL;
PRAGMA synchronous=NORMAL;
```

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Development Guidelines
- Follow PEP 8 for Python code
- Use Flutter/Dart style guidelines
- Write tests for new features
- Update documentation for API changes
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Getting Help
- **Issues**: [GitHub Issues](https://github.com/0xabhiram/food-yeh-backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/0xabhiram/food-yeh-backend/discussions)
- **Documentation**: Check this README and inline code comments

### Reporting Bugs
When reporting bugs, please include:
- Operating system and version
- Python/Flutter version
- Error messages and logs
- Steps to reproduce the issue

### Feature Requests
For feature requests, please:
- Check existing issues first
- Provide detailed description
- Explain the use case
- Consider contributing the feature yourself

---

**Built with ❤️ for smart vending solutions**

**Repository**: [https://github.com/0xabhiram/food-yeh-backend.git](https://github.com/0xabhiram/food-yeh-backend.git)
