# Foodyeh Backend Deployment Package

This repository contains all the necessary files to deploy the Foodyeh backend to a cloud server (Digital Ocean, AWS, etc.).

## 📁 Repository Structure

```
foodyeh-backend/
├── backend/                 # Main FastAPI application
│   ├── main.py             # FastAPI app entry point
│   ├── config.py           # Configuration settings
│   ├── requirements.txt    # Python dependencies
│   ├── auth/              # JWT authentication system
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   ├── utils/             # Helper functions
│   └── models/            # Data models
├── nginx/                  # Web server configuration
│   └── foodyeh.conf       # Nginx config with SSL
├── fail2ban/              # Security configuration
│   ├── foodyeh-api.conf   # Jail configuration
│   └── foodyeh-api.filter # Filter rules
├── systemd/               # Service files
│   ├── foodyeh-api.service
│   └── foodyeh-mqtt.service
├── scripts/               # Deployment scripts
│   ├── deploy_setup.sh    # Initial server setup
│   └── install_ssl.sh     # SSL certificate setup
└── .env.example           # Environment variables template
```

## 🚀 Quick Deployment

### 1. Clone this repository to your server
```bash
git clone https://github.com/your-username/foodyeh-backend.git
cd foodyeh-backend
```

### 2. Create environment file
```bash
cp .env.example .env
nano .env  # Edit with your production values
```

### 3. Run deployment script
```bash
chmod +x scripts/deploy_setup.sh
./scripts/deploy_setup.sh
```

### 4. Install SSL certificates
```bash
chmod +x scripts/install_ssl.sh
./scripts/install_ssl.sh
```

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost/foodyeh_db

# JWT Configuration
JWT_SECRET_KEY=your_super_secure_512_bit_jwt_secret_key_here
SECRET_KEY=your_super_secret_key_here_make_it_long_and_random

# MQTT Configuration
MQTT_BROKER_HOST=mqtt.foodyeh.io
MQTT_BROKER_PORT=8883
MQTT_USERNAME=your_mqtt_username
MQTT_PASSWORD=your_mqtt_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=false
ENFORCE_HTTPS=true

# Security
ALLOWED_ORIGINS=["https://api.foodyeh.io"]
ADMIN_WHITELIST_IPS=["your_admin_ip"]

# Redis
REDIS_URL=redis://localhost:6379
```

## 🔒 Security Features

- ✅ HTTPS enforcement
- ✅ Security headers (CSP, HSTS, X-Frame-Options)
- ✅ Rate limiting
- ✅ JWT authentication with HS512
- ✅ Fail2Ban protection
- ✅ IP whitelisting
- ✅ Structured logging
- ✅ Global exception handling

## 📊 API Endpoints

- `POST /api/v1/auth/token` - Get JWT token
- `GET /api/v1/auth/me` - Get current user info
- `GET /api/v1/auth/verify` - Verify token
- `POST /api/v1/auth/change-password` - Change password
- `GET /api/v1/status/health` - Health check
- `GET /api/v1/status/mqtt` - MQTT status
- `GET /api/v1/admin/system-info` - System information
- `POST /api/v1/admin/reboot` - Reboot device
- `POST /api/v1/admin/override` - Override MQTT
- `POST /api/v1/admin/clear-rate-limits` - Clear rate limits

## 🛠️ Services

- **FastAPI Backend**: Main application server
- **Nginx**: Reverse proxy and SSL termination
- **Redis**: Caching and rate limiting
- **PostgreSQL**: Database (optional, can use SQLite)
- **MQTT**: IoT communication
- **Fail2Ban**: Security monitoring

## 📝 Logs

Logs are stored in `/var/log/foodyeh/`:
- `api.log` - Security events for Fail2Ban
- `app.log` - Application logs
- `error.log` - Error logs

## 🔍 Monitoring

- Health check: `https://api.foodyeh.io/health`
- API docs: `https://api.foodyeh.io/docs` (if DEBUG=true)
- Logs: `/var/log/foodyeh/`

## 🚨 Troubleshooting

### Common Issues

1. **Port 8000 not accessible**
   - Check if uvicorn is running: `systemctl status foodyeh-api`
   - Check firewall: `ufw status`

2. **SSL certificate issues**
   - Run: `./scripts/install_ssl.sh`
   - Check: `nginx -t`

3. **Database connection errors**
   - Verify PostgreSQL is running
   - Check connection string in .env

4. **MQTT connection failed**
   - Verify MQTT broker credentials
   - Check network connectivity

### Useful Commands

```bash
# Check service status
systemctl status foodyeh-api
systemctl status nginx
systemctl status redis

# View logs
tail -f /var/log/foodyeh/api.log
journalctl -u foodyeh-api -f

# Restart services
systemctl restart foodyeh-api
systemctl restart nginx

# Check Fail2Ban
fail2ban-client status foodyeh-api
```

## 📞 Support

For issues or questions:
- Check logs in `/var/log/foodyeh/`
- Review security events in Fail2Ban
- Monitor system resources

## 🔄 Updates

To update the application:
```bash
git pull origin main
systemctl restart foodyeh-api
```

## 📄 License

This project is proprietary software for Foodyeh vending machine system. 