# Foodyeh FastAPI Backend

Production-ready FastAPI backend for the Foodyeh smart vending machine system with comprehensive security features.

## 🏗️ Architecture

```
backend/
├── main.py                 # FastAPI application entry point
├── config.py              # Configuration and settings
├── requirements.txt       # Python dependencies
├── env.example           # Environment variables template
├── routers/              # API route handlers
│   ├── order.py         # Order management endpoints
│   ├── status.py        # Status and health check endpoints
│   └── admin.py         # Admin and system control endpoints
├── services/             # Business logic services
│   ├── auth.py          # JWT authentication service
│   └── mqtt_client.py   # MQTT communication service
├── models/               # Data models and schemas
│   └── order.py         # Order and status models
└── utils/                # Utility functions
    └── rate_limiter.py  # Rate limiting implementation
```

## 🔒 Security Features

### Authentication & Authorization
- **JWT Token Authentication**: All API endpoints require valid JWT tokens
- **Role-based Access Control**: Admin endpoints require admin privileges
- **IP Whitelisting**: Admin endpoints restricted to whitelisted IP addresses
- **Token Expiration**: Configurable token expiration (default: 30 minutes)

### Rate Limiting
- **IP-based Rate Limiting**: Per-minute and per-hour limits
- **Token-based Rate Limiting**: Additional limits per authenticated user
- **Redis Backend**: Scalable rate limiting with Redis
- **Configurable Limits**: Adjustable limits for different endpoints

### Input Validation & Sanitization
- **Pydantic Models**: Comprehensive request/response validation
- **SQL Injection Prevention**: Parameterized queries and input sanitization
- **XSS Prevention**: Input sanitization and output encoding
- **Request Size Limits**: Protection against large payload attacks

### Security Headers
- **CORS Protection**: Restricted to specified origins
- **Security Headers**: XSS, CSRF, and other security headers
- **HTTPS Enforcement**: Strict Transport Security headers
- **Content Security Policy**: CSP headers for XSS protection

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Redis server
- MQTT broker (mqtt.foodyeh.io:8883)

### Installation

1. **Clone and setup**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**:
```bash
cp env.example /etc/foodyeh.env
# Edit /etc/foodyeh.env with your production values
```

3. **Start the server**:
```bash
python main.py
```

### Development Mode
```bash
# Set environment variable for development
export ENVIRONMENT=development
python main.py
```

## 📋 API Endpoints

### Public Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /api/info` - API details

### Protected Endpoints (Require JWT)

#### Order Management
- `POST /api/v1/order/` - Create new order
- `GET /api/v1/order/{order_id}` - Get order status
- `GET /api/v1/order/` - List user orders
- `PUT /api/v1/order/{order_id}/status` - Update order status
- `DELETE /api/v1/order/{order_id}` - Cancel order

#### Status & Health
- `GET /api/v1/status/health` - Detailed health check
- `GET /api/v1/status/mqtt` - MQTT connection status
- `GET /api/v1/status/order/{order_id}` - Detailed order status
- `GET /api/v1/status/system` - System status information
- `GET /api/v1/status/rate-limits` - Rate limit information

#### Admin Endpoints (Require Admin + IP Whitelist)
- `GET /api/v1/admin/logs` - Get admin logs
- `POST /api/v1/admin/reboot` - Reboot device
- `POST /api/v1/admin/override` - Send override command
- `GET /api/v1/admin/system-info` - System information
- `POST /api/v1/admin/clear-rate-limits` - Clear rate limits
- `GET /api/v1/admin/audit-trail` - Audit trail

## 🔧 Configuration

### Environment Variables

Create `/etc/foodyeh.env` with the following variables:

```bash
# Required
SECRET_KEY=your-super-secret-key-at-least-32-characters-long
MQTT_BROKER=mqtt.foodyeh.io
MQTT_PORT=8883
REDIS_URL=redis://localhost:6379

# Optional (with defaults)
DEBUG=false
LOG_LEVEL=INFO
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
ALLOWED_ORIGINS=["https://tablet.foodyeh.io"]
ADMIN_WHITELIST_IPS=["192.168.1.100"]
```

### Security Configuration

1. **Generate a strong secret key**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

2. **Configure admin IP whitelist**:
```bash
# Add your admin IP addresses
ADMIN_WHITELIST_IPS=["192.168.1.100", "10.0.0.50"]
```

3. **Set up CORS origins**:
```bash
ALLOWED_ORIGINS=["https://tablet.foodyeh.io"]
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 foodyeh && chown -R foodyeh:foodyeh /app
USER foodyeh

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    env_file:
      - /etc/foodyeh.env
    depends_on:
      - redis
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

## 🔄 Nginx Configuration

### SSL Termination with Let's Encrypt

```nginx
server {
    listen 80;
    server_name api.foodyeh.io;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.foodyeh.io;

    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/api.foodyeh.io/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.foodyeh.io/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # Security Headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Rate Limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 30s;
        proxy_send_timeout 30s;
        proxy_read_timeout 30s;
    }

    # Health check endpoint
    location /health {
        access_log off;
        proxy_pass http://127.0.0.1:8000/health;
    }
}
```

## 🔍 Monitoring & Logging

### Structured Logging
The application uses `structlog` for structured JSON logging:

```json
{
  "timestamp": "2024-01-15T10:30:00.123Z",
  "level": "info",
  "logger": "main",
  "event": "Request completed",
  "method": "POST",
  "url": "/api/v1/order/",
  "status_code": 201,
  "process_time": 0.123,
  "client_ip": "192.168.1.100"
}
```

### Health Monitoring
- **Health Check**: `GET /health` - Basic health status
- **Detailed Health**: `GET /api/v1/status/health` - Comprehensive health check
- **MQTT Status**: `GET /api/v1/status/mqtt` - MQTT connection status

### Metrics
- Request count and response times
- Rate limiting statistics
- MQTT connection status
- Error rates and types

## 🛡️ Security Best Practices

### Production Checklist
- [ ] Use strong, unique secret keys
- [ ] Configure admin IP whitelist
- [ ] Enable HTTPS with valid certificates
- [ ] Set up proper CORS origins
- [ ] Configure rate limiting
- [ ] Enable structured logging
- [ ] Set up monitoring and alerting
- [ ] Regular security updates
- [ ] Database backups
- [ ] SSL/TLS configuration

### Security Headers
The application automatically adds security headers:
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`

## 🧪 Testing

### Run Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### API Testing
```bash
# Test health endpoint
curl https://api.foodyeh.io/health

# Test with authentication
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     https://api.foodyeh.io/api/v1/order/
```

## 📚 API Documentation

When running in development mode, API documentation is available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🚨 Troubleshooting

### Common Issues

1. **MQTT Connection Failed**
   - Check MQTT broker credentials
   - Verify network connectivity
   - Check SSL certificate validity

2. **Rate Limiting Issues**
   - Verify Redis connection
   - Check rate limit configuration
   - Monitor Redis memory usage

3. **Authentication Errors**
   - Verify JWT token format
   - Check token expiration
   - Validate secret key configuration

4. **Admin Access Denied**
   - Verify admin role in JWT token
   - Check IP whitelist configuration
   - Ensure proper authentication

### Log Analysis
```bash
# View application logs
tail -f /var/log/foodyeh/api.log

# Search for errors
grep "ERROR" /var/log/foodyeh/api.log

# Monitor rate limiting
grep "Rate limit exceeded" /var/log/foodyeh/api.log
```

## 📄 License

This project is proprietary software for Foodyeh smart vending machine system.

## 🤝 Contributing

For internal development:
1. Follow the existing code style
2. Add comprehensive tests
3. Update documentation
4. Ensure security best practices
5. Test thoroughly before deployment 