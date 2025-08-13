# 🍔 Foodyeh - Smart Vending Machine Management System

A comprehensive smart vending machine management system with Flutter frontend and FastAPI backend, featuring real-time MQTT communication, secure authentication, and admin dashboard.

## 🚀 Features

### Frontend (Flutter)
- **Cross-platform mobile app** (Android, iOS, Web, Windows)
- **Modern UI/UX** with dark theme and Material Design 3
- **Real-time updates** via MQTT WebSocket connection
- **Secure authentication** with JWT tokens
- **Role-based access control** (Admin/User)
- **Order management** and status tracking
- **Cart functionality** with persistent storage
- **Profile management** and settings

### Backend (FastAPI)
- **RESTful API** with automatic documentation
- **JWT authentication** with refresh tokens
- **Role-based access control** (RBAC)
- **MQTT integration** for real-time communication
- **SQLite database** (easily swappable to PostgreSQL)
- **File upload handling** with security validation
- **Rate limiting** and brute force protection
- **OWASP Top-10 security** compliance
- **Comprehensive logging** and monitoring

### DevOps & Security
- **Production-ready deployment** configuration
- **Nginx reverse proxy** with SSL/TLS
- **Docker containerization** support
- **Fail2ban intrusion prevention**
- **Automated backups** and log rotation
- **Health checks** and monitoring

## 📋 Prerequisites

- **Flutter SDK** (3.8.0 or higher)
- **Python** (3.8 or higher)
- **Git**
- **Android Studio** (for mobile development)
- **PostgreSQL** (optional, for production)

## 🛠️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/foodyeh-poc-1.git
cd foodyeh-poc-1
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp env_example.txt .env
# Edit .env with your configuration

# Initialize database
python seed_data.py

# Run the backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. Frontend Setup
```bash
cd frontend

# Get Flutter dependencies
flutter pub get

# Run the app
flutter run
```

### 4. MQTT Setup (Optional)
```bash
# Install Mosquitto MQTT broker
sudo apt-get install mosquitto mosquitto-clients

# Configure Mosquitto (see DEPLOY.md for details)
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

## 🔐 Default Credentials

### Admin Account
```
Email: admin@foodyeh.io
Password: ChangeThisPassword123!
```

### Alternative Admin Account
```
Email: admin@foodyeh.com
Password: Admin123!
```

**⚠️ Important:** Change these passwords immediately after first login!

## 📱 Usage

### For Users
1. **Login** with your credentials
2. **Browse dishes** in the home screen
3. **Add items** to cart
4. **Place orders** and track status
5. **View order history** in profile

### For Admins
1. **Login** with admin credentials
2. **Access admin dashboard**
3. **Manage dishes** (add, edit, delete)
4. **View all orders** and update status
5. **Monitor system health**
6. **Manage users** and permissions

## 🏗️ Project Structure

```
foodyeh-poc-1/
├── frontend/                 # Flutter application
│   ├── lib/
│   │   ├── core/            # Core utilities and constants
│   │   ├── models/          # Data models
│   │   ├── provider/        # State management
│   │   ├── screens/         # UI screens
│   │   ├── services/        # API services
│   │   ├── utils/           # Utility functions
│   │   └── widgets/         # Reusable widgets
│   ├── android/             # Android-specific files
│   ├── ios/                 # iOS-specific files
│   └── web/                 # Web-specific files
├── backend/                 # FastAPI application
│   ├── app/
│   │   ├── routers/         # API routes
│   │   ├── models/          # Database models
│   │   ├── services/        # Business logic
│   │   ├── utils/           # Utility functions
│   │   └── middleware/      # Custom middleware
│   ├── auth/                # Authentication module
│   └── tests/               # Backend tests
├── nginx/                   # Nginx configuration
├── scripts/                 # Deployment scripts
├── systemd/                 # Systemd service files
└── docs/                    # Documentation
```

## 🔧 Configuration

### Environment Variables
Key environment variables for the backend:

```env
# API Configuration
API_BASE=https://api.foodyeh.io
DEBUG=false
ENVIRONMENT=production

# Database
DB_URL=sqlite+aiosqlite:///./foodyeh.db

# JWT Settings
JWT_SECRET=your-super-secret-jwt-key-64-characters-minimum
JWT_ALGO=HS512
ACCESS_TTL_MIN=15
REFRESH_TTL_DAYS=7

# MQTT Configuration
MQTT_HOST=api.foodyeh.io
MQTT_PORT=443
MQTT_USE_WEBSOCKETS=true
MQTT_WS_PATH=/mqtt
MQTT_USE_TLS=true

# Security
RATE_LIMIT_AUTH=5
RATE_LIMIT_API=300
ACCOUNT_LOCKOUT_ATTEMPTS=5
ACCOUNT_LOCKOUT_DURATION=600
```

## 🚀 Deployment

For production deployment, see [DEPLOY.md](DEPLOY.md) for detailed instructions including:

- **Ubuntu server setup**
- **Nginx configuration**
- **SSL/TLS setup**
- **Systemd services**
- **Security hardening**
- **Monitoring and logging**

## 🧪 Testing

### Backend Tests
```bash
cd backend
python -m pytest tests/
```

### Frontend Tests
```bash
cd frontend
flutter test
```

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔒 Security Features

- **JWT Authentication** with secure token handling
- **Rate Limiting** to prevent brute force attacks
- **Input Validation** and sanitization
- **CORS Protection** with secure origins
- **SQL Injection Prevention** with parameterized queries
- **XSS Protection** with content security policies
- **File Upload Security** with type and size validation
- **Account Lockout** after failed login attempts

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues:

1. Check the [Issues](https://github.com/yourusername/foodyeh-poc-1/issues) page
2. Review the [DEPLOY.md](DEPLOY.md) for deployment issues
3. Check the logs in `/var/log/foodyeh/` for backend issues

## 🎯 Roadmap

- [ ] **Mobile app** for vending machine interface
- [ ] **Payment integration** (Stripe, PayPal)
- [ ] **Inventory management** with low stock alerts
- [ ] **Analytics dashboard** with sales reports
- [ ] **Multi-language support**
- [ ] **Push notifications**
- [ ] **Offline mode** support
- [ ] **QR code** payment system

---

**Built with ❤️ for smart vending solutions**
