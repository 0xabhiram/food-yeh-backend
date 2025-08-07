# Communication Guide: Flutter UI ↔ MQTT ↔ FastAPI Server

## Overview
This guide explains how the three main components of your Foodyeh system communicate with each other in the production environment.

## Architecture Diagram
```
┌─────────────────┐    HTTPS/API    ┌─────────────────┐
│   Flutter UI    │ ◄──────────────► │   FastAPI       │
│   (Admin Panel) │                 │   Server        │
└─────────────────┘                 └─────────────────┘
         │                                   │
         │                                   │
         │ MQTT (Optional)                   │ MQTT
         │                                   │
         └───────────────────────────────────┼──┘
                                            │
                                            ▼
                                    ┌─────────────────┐
                                    │   MQTT Broker   │
                                    │   (Mosquitto)   │
                                    └─────────────────┘
                                            │
                                            │ MQTT
                                            ▼
                                    ┌─────────────────┐
                                    │  Vending        │
                                    │  Machine        │
                                    │  Hardware       │
                                    └─────────────────┘
```

## 1. Flutter UI ↔ FastAPI Server Communication

### API Endpoints Used by Flutter App

#### Authentication
```dart
// Login
POST https://api.your-domain.com/api/v1/auth/login
{
  "username": "admin",
  "password": "password"
}

// Response
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

#### Dashboard Data
```dart
// Health Status
GET https://api.your-domain.com/api/v1/status/health
Authorization: Bearer <token>

// MQTT Status
GET https://api.your-domain.com/api/v1/status/mqtt
Authorization: Bearer <token>

// System Info
GET https://api.your-domain.com/api/v1/admin/system-info
Authorization: Bearer <token>

// Recent Orders
GET https://api.your-domain.com/api/v1/orders?limit=10
Authorization: Bearer <token>
```

#### Food Items Management
```dart
// Get all items
GET https://api.your-domain.com/api/v1/food-items
Authorization: Bearer <token>

// Create item
POST https://api.your-domain.com/api/v1/food-items
Authorization: Bearer <token>
{
  "name": "Coca Cola",
  "price": 2.50,
  "slotId": "A1",
  "imageUrl": "https://example.com/cola.jpg"
}

// Update item
PUT https://api.your-domain.com/api/v1/food-items/{id}
Authorization: Bearer <token>

// Delete item
DELETE https://api.your-domain.com/api/v1/food-items/{id}
Authorization: Bearer <token>
```

#### Admin Controls
```dart
// Reboot device
POST https://api.your-domain.com/api/v1/admin/reboot
Authorization: Bearer <token>

// Override MQTT commands
POST https://api.your-domain.com/api/v1/admin/override
Authorization: Bearer <token>
{
  "command": "dispense",
  "slot": "A1"
}

// Clear rate limits
POST https://api.your-domain.com/api/v1/admin/clear-rate-limits
Authorization: Bearer <token>
```

#### Logs and Audit
```dart
// Get admin logs
GET https://api.your-domain.com/api/v1/admin/logs?page=1&limit=50
Authorization: Bearer <token>

// Get audit trail
GET https://api.your-domain.com/api/v1/admin/audit-trail?page=1&limit=50
Authorization: Bearer <token>
```

### Error Handling in Flutter
```dart
// Example error handling in ApiService
try {
  final response = await _dio.get('/api/v1/status/health');
  return HealthCheck.fromJson(response.data);
} on DioException catch (e) {
  if (e.response?.statusCode == 401) {
    // Token expired, try refresh
    await _refreshToken();
    // Retry request
    return await _makeRequest(() => _dio.get('/api/v1/status/health'));
  }
  throw ApiException(e.message);
}
```

## 2. FastAPI Server ↔ MQTT Broker Communication

### MQTT Topics Used

#### System Status Topics
```
foodyeh/status/health          # Health status updates
foodyeh/status/mqtt           # MQTT connection status
foodyeh/status/system         # System information
foodyeh/status/device         # Device status
```

#### Order Management Topics
```
foodyeh/orders/new            # New order received
foodyeh/orders/status         # Order status updates
foodyeh/orders/completed      # Order completed
foodyeh/orders/failed         # Order failed
```

#### Inventory Topics
```
foodyeh/inventory/update      # Inventory level updates
foodyeh/inventory/low         # Low stock alerts
foodyeh/inventory/out         # Out of stock alerts
```

#### Control Topics
```
foodyeh/control/reboot        # Reboot command
foodyeh/control/override      # Override commands
foodyeh/control/clear-limits  # Clear rate limits
```

### FastAPI MQTT Integration Example
```python
# In your FastAPI backend
import paho.mqtt.client as mqtt
from fastapi import FastAPI

app = FastAPI()
mqtt_client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with code: {rc}")
    client.subscribe("foodyeh/orders/new")
    client.subscribe("foodyeh/status/device")

def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()
    
    if topic == "foodyeh/orders/new":
        # Handle new order
        process_new_order(payload)
    elif topic == "foodyeh/status/device":
        # Update device status
        update_device_status(payload)

@app.on_event("startup")
async def startup_event():
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set("admin", "your_mqtt_password")
    mqtt_client.connect("localhost", 1883, 60)
    mqtt_client.loop_start()

@app.post("/api/v1/admin/reboot")
async def reboot_device():
    # Publish reboot command to MQTT
    mqtt_client.publish("foodyeh/control/reboot", "reboot")
    return {"message": "Reboot command sent"}
```

## 3. MQTT Broker ↔ Vending Machine Hardware

### Hardware Communication Topics
```
foodyeh/hardware/status       # Hardware status
foodyeh/hardware/temperature  # Temperature readings
foodyeh/hardware/door         # Door open/close events
foodyeh/hardware/error        # Hardware errors
```

### Command Topics
```
foodyeh/commands/dispense     # Dispense item command
foodyeh/commands/light        # Control lighting
foodyeh/commands/display      # Update display
foodyeh/commands/reboot       # Reboot hardware
```

## 4. Production Configuration

### Environment Variables for Communication

#### FastAPI Server (.env)
```env
# MQTT Configuration
MQTT_BROKER_HOST=localhost
MQTT_BROKER_PORT=1883
MQTT_USERNAME=admin
MQTT_PASSWORD=your_mqtt_password

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
ENFORCE_HTTPS=true

# CORS for Flutter app
ALLOWED_ORIGINS=["https://your-domain.com", "https://admin.your-domain.com"]
```

#### Flutter App (app_constants.dart)
```dart
// Production API URL
static const String baseUrl = 'https://api.your-domain.com';

// MQTT Configuration (if direct MQTT access needed)
static const String mqttBroker = 'mqtt.your-domain.com';
static const int mqttPort = 1883;
static const String mqttUsername = 'admin';
static const String mqttPassword = 'your_mqtt_password';
```

### Network Configuration

#### Firewall Rules
```bash
# Allow HTTP/HTTPS for API
sudo ufw allow 80
sudo ufw allow 443

# Allow MQTT (if external access needed)
sudo ufw allow 1883

# Allow WebSocket for MQTT (if needed)
sudo ufw allow 9001
```

#### Nginx Configuration for API
```nginx
# API Proxy
location /api/ {
    proxy_pass http://127.0.0.1:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # CORS headers
    add_header Access-Control-Allow-Origin *;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
    add_header Access-Control-Allow-Headers "Authorization, Content-Type";
}
```

## 5. Security Considerations

### API Security
- All API endpoints require JWT authentication
- HTTPS enforcement enabled
- Rate limiting implemented
- CORS properly configured

### MQTT Security
- Authentication required (no anonymous access)
- Username/password authentication
- SSL/TLS encryption (if external access)

### Network Security
- Firewall configured
- Only necessary ports open
- SSL certificates installed

## 6. Monitoring and Debugging

### API Monitoring
```bash
# Check API logs
tail -f /var/log/foodyeh/api.log

# Check API status
curl https://api.your-domain.com/health

# Check supervisor status
sudo supervisorctl status foodyeh-api
```

### MQTT Monitoring
```bash
# Check MQTT logs
tail -f /var/log/mosquitto/mosquitto.log

# Test MQTT connection
mosquitto_pub -h localhost -p 1883 -u admin -P your_password -t test/topic -m "test"

# Subscribe to topics
mosquitto_sub -h localhost -p 1883 -u admin -P your_password -t foodyeh/#
```

### Flutter App Debugging
```dart
// Enable debug logging
static const bool enableDebugLogs = true;

// Log API requests
if (enableDebugLogs) {
  print('API Request: ${request.url}');
  print('API Response: ${response.data}');
}
```

## 7. Troubleshooting Common Issues

### API Connection Issues
1. Check if FastAPI server is running
2. Verify firewall settings
3. Check SSL certificate validity
4. Verify domain DNS settings

### MQTT Connection Issues
1. Check if Mosquitto is running
2. Verify credentials in password file
3. Check MQTT port accessibility
4. Verify topic subscriptions

### Flutter App Issues
1. Check API base URL configuration
2. Verify JWT token validity
3. Check network connectivity
4. Review error logs

## 8. Performance Optimization

### API Optimization
- Enable response caching
- Use connection pooling
- Implement pagination
- Optimize database queries

### MQTT Optimization
- Use QoS levels appropriately
- Implement message persistence
- Monitor broker performance
- Clean up old messages

### Network Optimization
- Use CDN for static assets
- Enable gzip compression
- Optimize SSL configuration
- Monitor bandwidth usage

This communication guide ensures all components work together seamlessly in your production environment. 