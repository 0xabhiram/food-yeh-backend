# Backend Deployment Package for Digital Ocean

## Files to Include in Cloud Deployment

### Core Application Files
- `main.py` - Main FastAPI application
- `config.py` - Configuration settings
- `database.py` - Database configuration
- `requirements.txt` - Python dependencies
- `logging_config.py` - Logging configuration

### Authentication System
- `auth/` - Complete authentication package
  - `auth/__init__.py`
  - `auth/jwt_handler.py`
  - `auth/models.py`
  - `auth/routes.py`

### API Routers
- `routers/` - API endpoints
  - `routers/order.py`
  - `routers/status.py`
  - `routers/admin.py`

### Services
- `services/` - Business logic
  - `services/mqtt_client.py`
  - `services/auth.py`

### Utilities
- `utils/` - Helper functions
  - `utils/rate_limiter.py`

### Models
- `models/` - Data models
  - All model files

### Configuration Files
- `.env` - Environment variables (create on server)
- `nginx/` - Nginx configuration
- `fail2ban/` - Security configuration

### Documentation
- `README.md` - Setup instructions
- `SECURITY_UPDATES.md` - Security features
- `COMMUNICATION_GUIDE.md` - Architecture guide

## Files to EXCLUDE (Never deploy)
- `test_jwt.py` - Testing script only
- `env_test.txt` - Local testing only
- `__pycache__/` - Python cache
- `logs/` - Log files (created on server)
- `.git/` - Version control
- Any files with hardcoded secrets

## Environment Variables to Set on Server
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/foodyeh

# JWT Configuration
JWT_SECRET_KEY=your_super_secure_512_bit_jwt_secret_key_here
SECRET_KEY=your_super_secret_key_here_make_it_long_and_random

# MQTT Configuration
MQTT_BROKER_HOST=mqtt.foodyeh.io
MQTT_BROKER_PORT=8883
MQTT_USERNAME=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password

# Redis Configuration
REDIS_URL=redis://localhost:6379

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
ENFORCE_HTTPS=true

# Security
ALLOWED_ORIGINS=["https://your-domain.com"]
ADMIN_WHITELIST_IPS=["your_admin_ip"]

# Logging
LOG_LEVEL=INFO
```

## Deployment Steps
1. Upload backend folder to server
2. Create `.env` file with production values
3. Install dependencies: `pip install -r requirements.txt`
4. Setup Nginx configuration
5. Setup Fail2Ban
6. Start the application 