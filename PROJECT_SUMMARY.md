# Foodyeh POC - Project Summary

## 🎯 Project Overview

Foodyeh is a smart vending machine management system built with **Flutter** (frontend) and **FastAPI** (backend), featuring MQTT integration for real-time device communication. The system supports both user and admin roles with comprehensive security features.

## 🏗️ Architecture

### Backend (FastAPI)
- **Framework**: FastAPI with Python 3.11
- **Database**: SQLite (easily swappable to PostgreSQL)
- **Authentication**: JWT with refresh tokens
- **Security**: OWASP Top-10 compliant with rate limiting, input validation, and security headers
- **MQTT**: Local Mosquitto broker for device communication
- **Caching**: Redis for rate limiting and session management

### Frontend (Flutter)
- **Framework**: Flutter 3.0+
- **State Management**: Provider pattern
- **Navigation**: GoRouter for declarative routing
- **Theme**: Custom dark theme with Foodyeh branding
- **HTTP Client**: Dio with automatic token refresh

## 🔐 Security Features

### Authentication & Authorization
- JWT tokens with 15-minute access and 7-day refresh
- Role-based access control (user/admin)
- Password hashing with bcrypt
- Account lockout after 5 failed attempts
- Rate limiting on auth endpoints

### Data Protection
- Input validation with Pydantic schemas
- SQL injection prevention with SQLAlchemy ORM
- XSS protection with security headers
- CORS configuration
- No sensitive data in logs

## 📱 User Features

### Authentication
- Login/Signup with email validation
- Password strength requirements
- Automatic token refresh
- Secure logout

### Menu Browsing
- Grid view of 14 pre-loaded dishes
- Search functionality
- Category filtering
- Dish details with images

### Shopping Cart
- Add/remove items
- Quantity adjustment
- Real-time total calculation
- Checkout process

### Order Management
- Order history
- Real-time status updates
- Order details with items
- Payment processing (dummy)

### Profile Management
- User information display
- Account settings
- Quick navigation

## 👨‍💼 Admin Features

### Dashboard
- Real-time statistics
- Revenue tracking
- Order status breakdown
- User activity overview

### User Management
- View all users
- Toggle user status
- Role management
- User analytics

### Menu Management
- CRUD operations on dishes
- Image upload functionality
- Price and availability management
- Category organization

### Order Management
- View all orders
- Status updates
- Order filtering
- Payment tracking

## 🔌 MQTT Integration

### Topics
- **Commands**: `vending/commands/{deviceId}` - Send orders to devices
- **Status**: `vending/status/{deviceId}/{orderId}` - Receive device updates

### Message Format
```json
// Command
{
  "orderId": 123,
  "items": [{"dishId": 1, "qty": 2}],
  "ts": "2024-01-01T12:00:00Z"
}

// Status Update
{
  "state": "preparing",
  "ts": "2024-01-01T12:05:00Z",
  "message": "Cooking in progress"
}
```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp env.example .env
# Edit .env with your configuration
python seed_data.py
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
flutter pub get
flutter run
```

### MQTT Setup
```bash
# Install Mosquitto
sudo apt install mosquitto mosquitto-clients

# Start broker
mosquitto -c mosquitto.conf
```

## 📊 Sample Data

### Admin User
- **Email**: admin@foodyeh.com
- **Password**: Admin123!

### Sample Dishes (14 items)
1. Margherita Pizza - $12.99
2. Pepperoni Pizza - $14.99
3. BBQ Chicken Pizza - $16.99
4. Classic Burger - $11.99
5. Chicken Burger - $10.99
6. Veggie Burger - $12.99
7. Caesar Salad - $8.99
8. Greek Salad - $9.99
9. Chicken Wings - $13.99
10. Mozzarella Sticks - $7.99
11. Chocolate Brownie - $6.99
12. Cheesecake - $7.99
13. Soft Drink - $2.99
14. Fresh Juice - $4.99

## 🔧 API Endpoints

### Authentication
- `POST /auth/signup` - User registration
- `POST /auth/login` - User login
- `POST /auth/refresh` - Refresh token
- `POST /auth/logout` - User logout

### Dishes
- `GET /dishes` - List all dishes
- `GET /dishes/{id}` - Get specific dish
- `POST /dishes` - Create dish (admin)
- `PUT /dishes/{id}` - Update dish (admin)
- `DELETE /dishes/{id}` - Delete dish (admin)

### Orders
- `POST /orders` - Create order
- `GET /orders/me` - User's orders
- `GET /orders/{id}` - Get specific order
- `POST /orders/{id}/pay` - Process payment

### Admin
- `GET /admin/users` - List all users
- `GET /admin/orders` - List all orders
- `GET /admin/dashboard/stats` - Dashboard statistics

## 🐳 Docker Support

### Development
```bash
docker-compose -f docker-compose.dev.yml up
```

### Production
```bash
# Build and run with Docker
docker build -t foodyeh-backend ./backend
docker run -p 8000:8000 foodyeh-backend
```

## 📈 Performance Features

### Backend
- Async/await for non-blocking operations
- Database connection pooling
- Redis caching for rate limiting
- Optimized SQL queries

### Frontend
- Lazy loading for images
- Efficient state management
- Optimized navigation
- Responsive design

## 🔍 Monitoring & Logging

### Backend Logging
- Structured logging with different levels
- Request/response logging
- Error tracking
- Performance metrics

### Health Checks
- `/health` endpoint for monitoring
- Database connectivity checks
- MQTT connection status
- Service health indicators

## 🛡️ Production Deployment

### Security Checklist
- [ ] Change default JWT secret
- [ ] Configure HTTPS with SSL certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Configure backup strategy
- [ ] Set up monitoring and alerting
- [ ] Enable fail2ban
- [ ] Configure log rotation

### Performance Optimization
- [ ] Database indexing
- [ ] Redis caching
- [ ] CDN for static assets
- [ ] Gzip compression
- [ ] Load balancing (if needed)

## 🧪 Testing

### Backend Testing
```bash
cd backend
pytest tests/
```

### Frontend Testing
```bash
cd frontend
flutter test
```

## 📚 Documentation

- **API Documentation**: Available at `/docs` when running FastAPI
- **Deployment Guide**: See `DEPLOY.md`
- **Security Guide**: See `SECURITY.md`

## 🔄 Future Enhancements

### Planned Features
- Real-time notifications
- Push notifications
- Advanced analytics
- Multi-language support
- Offline mode
- Payment gateway integration
- Inventory management
- Device monitoring dashboard

### Scalability Improvements
- PostgreSQL migration
- Microservices architecture
- Message queue (RabbitMQ/Apache Kafka)
- Container orchestration (Kubernetes)
- CDN integration
- Database sharding

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the deployment guide

---

**Foodyeh POC** - Smart Vending Machine Management System  
*Built with ❤️ using Flutter & FastAPI*
