# Security Enhancements for Foodyeh FastAPI Backend

## Overview
This document outlines the comprehensive security enhancements implemented for the Foodyeh FastAPI backend, making it production-ready and attack-resilient.

## 🔒 Security Features Implemented

### 1. HTTPS Enforcement
- **Nginx Configuration**: All HTTP traffic redirected to HTTPS
- **FastAPI Middleware**: Application-level HTTPS enforcement
- **Security Headers**: Comprehensive security headers implementation

### 2. Security Headers
```nginx
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
add_header Content-Security-Policy "default-src 'self'";
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "geolocation=(), microphone=(), camera=()" always;
```

### 3. Global Exception Handler
```python
@app.exception_handler(Exception)
async def safe_error_handler(request: Request, exc: Exception):
    """Global exception handler to prevent information leakage."""
    # Log actual error for debugging (but don't expose it)
    logger.error("Unhandled exception", ...)
    
    # Return safe error message
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred."}
    )
```

### 4. Fail2Ban Integration
- **Jail Configuration**: `/etc/fail2ban/jail.d/foodyeh-api.conf`
- **Filter Configuration**: `/etc/fail2ban/filter.d/foodyeh-api.conf`
- **Log Monitoring**: Structured JSON logs for security events
- **Auto-banning**: Blocks IPs after 5 failed attempts in 10 minutes

### 5. Structured JSON Logging
- **Security Events**: All security events logged with structured JSON
- **Fail2Ban Integration**: Logs formatted for Fail2Ban parsing
- **Event Types**: `unauthorized_access`, `auth_failure`, `https_violation`, `application_error`

## 📁 Modified Files

### Backend Files
1. **`backend/main.py`**
   - Added global exception handler
   - Enhanced security logging
   - HTTPS enforcement middleware
   - Security headers middleware

2. **`backend/logging_config.py`** (New)
   - Structured JSON logging configuration
   - Security event logging functions
   - Fail2Ban integration utilities

3. **`backend/config.py`**
   - Enhanced security settings
   - HTTPS enforcement configuration

### Nginx Configuration
4. **`nginx/foodyeh.conf`** (New)
   - HTTPS enforcement
   - Comprehensive security headers
   - Rate limiting
   - File access restrictions
   - CORS configuration

### Fail2Ban Configuration
5. **`fail2ban/foodyeh-api.conf`** (New)
   - Jail configuration for API security
   - IP whitelisting support
   - Ban actions and timing

6. **`fail2ban/foodyeh-api.filter`** (New)
   - JSON log parsing
   - Security event detection
   - IP extraction patterns

### Deployment Script
7. **`deploy_setup.sh`** (Updated)
   - Fail2Ban installation and configuration
   - Enhanced Nginx security setup
   - Security monitoring setup

## 🛡️ Security Features

### Authentication & Authorization
- JWT-based authentication
- Role-based access control
- IP whitelisting for admin endpoints
- Rate limiting on all endpoints

### Network Security
- HTTPS enforcement
- CORS protection
- Request size limits
- Proxy security headers

### Application Security
- Input validation with Pydantic
- SQL injection prevention
- XSS protection headers
- CSRF protection

### Monitoring & Logging
- Structured JSON logging
- Security event tracking
- Fail2Ban integration
- Comprehensive audit trail

## 🔧 Configuration Details

### Nginx Security Headers
```nginx
# Content Security Policy
add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-ancestors 'none';" always;

# Other Security Headers
add_header X-Content-Type-Options nosniff;
add_header X-Frame-Options DENY;
add_header X-XSS-Protection "1; mode=block";
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

### Fail2Ban Configuration
```ini
[foodyeh-api]
enabled = true
port = http,https
filter = foodyeh-api
logpath = /var/log/foodyeh/api.log
maxretry = 5
findtime = 600
bantime = 3600
ignoreip = 127.0.0.1 ::1
banaction = ufw
```

### Security Logging
```python
# Security event logging
log_security_event(
    event="unauthorized_access",
    ip=client_ip,
    path=request.url.path,
    status_code=401,
    method=method,
    user_agent=user_agent
)
```

## 🚀 Deployment Instructions

### 1. Run Enhanced Setup Script
```bash
chmod +x deploy_setup.sh
./deploy_setup.sh
```

### 2. Configure SSL Certificate
```bash
sudo certbot --nginx -d your-domain.com
```

### 3. Update Domain Configuration
- Update domain names in Nginx configuration
- Update CORS origins in environment file
- Update API base URL in Flutter app

### 4. Monitor Security
```bash
# Check Fail2Ban status
sudo fail2ban-client status foodyeh-api

# View banned IPs
sudo fail2ban-client banned

# Monitor security logs
tail -f /var/log/foodyeh/api.log
```

## 📊 Security Monitoring

### Log Files
- `/var/log/foodyeh/api.log` - Security events for Fail2Ban
- `/var/log/foodyeh/app.log` - General application logs
- `/var/log/foodyeh/error.log` - Error logs

### Fail2Ban Commands
```bash
# Check status
sudo fail2ban-client status foodyeh-api

# View banned IPs
sudo fail2ban-client banned

# Unban IP
sudo fail2ban-client set foodyeh-api unbanip <IP>

# View jail configuration
sudo fail2ban-client get foodyeh-api failregex
```

### Security Event Types
1. **`unauthorized_access`** - 401/403 responses
2. **`auth_failure`** - Authentication failures
3. **`https_violation`** - Non-HTTPS requests
4. **`application_error`** - Unhandled exceptions
5. **`rate_limit_exceeded`** - Rate limit violations

## 🔍 Testing Security Features

### Test HTTPS Enforcement
```bash
curl -k http://your-domain.com/api/v1/status/health
# Should return 400 with "HTTPS required"
```

### Test Security Headers
```bash
curl -I https://your-domain.com/api/v1/status/health
# Should show all security headers
```

### Test Fail2Ban
```bash
# Make multiple failed requests
for i in {1..10}; do
  curl -X POST https://your-domain.com/api/v1/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"wrong"}'
done

# Check if IP is banned
sudo fail2ban-client status foodyeh-api
```

## 🛠️ Maintenance

### Regular Tasks
- Monitor security logs daily
- Review banned IPs weekly
- Update SSL certificates (automatic)
- Check Fail2Ban configuration monthly

### Security Updates
```bash
# Update system packages
sudo apt update && sudo apt upgrade

# Restart security services
sudo systemctl restart fail2ban
sudo systemctl restart nginx
sudo supervisorctl restart foodyeh-api
```

## ✅ Security Checklist

- [x] HTTPS enforcement implemented
- [x] Security headers configured
- [x] Global exception handler added
- [x] Fail2Ban integration complete
- [x] Structured JSON logging implemented
- [x] Rate limiting configured
- [x] CORS protection enabled
- [x] Input validation with Pydantic
- [x] No sensitive information leakage
- [x] Comprehensive audit logging
- [x] Production-ready configuration

## 🎯 Production Readiness

The backend is now **production-ready** with:
- **Comprehensive security** against common attacks
- **Real-time monitoring** with Fail2Ban
- **Structured logging** for security analysis
- **HTTPS enforcement** for all communications
- **Rate limiting** to prevent abuse
- **Information leakage prevention**

All security features are implemented and tested, making the system resilient against common attack vectors while maintaining full functionality for legitimate users. 