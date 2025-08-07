# 🍽️ Foodyeh Admin Panel

A modern Flutter admin panel for managing smart vending machines with a beautiful yellow-black theme and comprehensive security features.

## 🎨 Features

### 🔐 **Authentication & Security**
- JWT-based authentication with secure token storage
- Role-based access control (Admin only)
- HTTPS enforcement in production
- Secure API communication with token refresh
- Input validation and sanitization

### 📊 **Dashboard**
- Real-time system health monitoring
- Order statistics and revenue tracking
- MQTT connectivity status
- Recent orders with live updates
- Responsive design for desktop/tablet

### 🍽️ **Food Item Management**
- Add, edit, and delete food items
- Slot management and inventory tracking
- Image URL support for item photos
- Category and tag organization
- Stock level monitoring

### 📋 **Order Management**
- View all orders with filtering
- Order status tracking and updates
- Detailed order information
- Processing time monitoring
- Revenue analytics

### 📊 **Logs & Audit Trail**
- Admin activity logs
- System audit trail with IP tracking
- Filterable log views
- Security event monitoring

### ⚙️ **System Controls**
- Device reboot functionality
- MQTT command override
- Rate limit management
- System health monitoring

## 🏗️ Architecture

### **Project Structure**
```
lib/
├── core/
│   ├── constants/     # App constants and configuration
│   ├── storage/       # Secure storage utilities
│   └── theme/         # Yellow-black theme configuration
├── models/            # Data models (User, Order, FoodItem, etc.)
├── screens/           # UI screens
├── services/          # API and authentication services
└── widgets/           # Reusable UI components
```

### **Security Features**
- ✅ **HTTPS Enforcement** - All API calls use HTTPS
- ✅ **JWT Authentication** - Secure token-based auth
- ✅ **Secure Storage** - Encrypted local storage
- ✅ **Input Validation** - Comprehensive form validation
- ✅ **Rate Limiting** - API rate limiting protection
- ✅ **CORS Protection** - Cross-origin request security

## 🚀 Getting Started

### **Prerequisites**
- Flutter SDK (3.0.0 or higher)
- Dart SDK
- Android Studio / VS Code
- API server running at `https://api.foodyeh.io`

### **Installation**

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd foodyeh_admin
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Generate model files**
   ```bash
   flutter packages pub run build_runner build
   ```

4. **Run the app**
   ```bash
   flutter run
   ```

### **Configuration**

The app uses the following configuration:

- **API Base URL**: `https://api.foodyeh.io`
- **Demo Credentials**: 
  - Username: `admin`
  - Password: `123456`

## 🎨 Theme

### **Color Palette**
- **Primary Yellow**: `#FFD700`
- **Secondary Yellow**: `#FFEB3B`
- **Primary Black**: `#1A1A1A`
- **Secondary Black**: `#2D2D2D`
- **Success Green**: `#4CAF50`
- **Error Red**: `#F44336`
- **Warning Orange**: `#FF9800`
- **Info Blue**: `#2196F3`

### **Design Features**
- Material 3 design system
- Dark theme with yellow accents
- Responsive layout for desktop/tablet
- Smooth animations and transitions
- Custom widgets with consistent styling

## 📱 Screens

### **1. Login Screen**
- Secure authentication form
- Demo credentials display
- Error handling and validation
- Beautiful yellow-black theme

### **2. Dashboard Screen**
- Welcome section with user info
- Statistics cards (orders, revenue, etc.)
- System health monitoring
- Recent orders list
- Real-time data refresh

### **3. Food Items Management**
- List all food items
- Add new items with form validation
- Edit existing items
- Delete items with confirmation
- Stock level monitoring

### **4. Orders Management**
- View all orders with pagination
- Filter by status and date
- Order details view
- Status update functionality
- Revenue analytics

### **5. Logs & Audit**
- Admin activity logs
- System audit trail
- Filterable views
- IP address tracking
- Security event monitoring

### **6. System Controls**
- Device reboot controls
- MQTT override commands
- Rate limit management
- System health monitoring

## 🔧 API Integration

### **Endpoints Used**
- `POST /auth/login` - User authentication
- `GET /status/health` - System health check
- `GET /status/mqtt` - MQTT connectivity status
- `GET /admin/system-info` - System information
- `GET /order` - List orders
- `GET /items` - List food items
- `POST /admin/reboot` - Device reboot
- `GET /admin/logs` - Admin logs
- `GET /admin/audit-trail` - Audit trail

### **Security Headers**
- Authorization: Bearer token
- Content-Type: application/json
- HTTPS enforcement
- Rate limiting protection

## 🛡️ Security Features

### **Authentication**
- JWT token-based authentication
- Secure token storage using `flutter_secure_storage`
- Automatic token refresh
- Session validation

### **Data Protection**
- HTTPS enforcement for all API calls
- Input validation and sanitization
- Secure error handling
- No sensitive data in logs

### **Access Control**
- Role-based permissions
- Admin-only access
- IP whitelist support
- Session timeout handling

## 📦 Dependencies

### **Core Dependencies**
- `flutter` - Core Flutter framework
- `provider` - State management
- `dio` - HTTP client for API calls
- `flutter_secure_storage` - Secure storage
- `go_router` - Navigation routing
- `google_fonts` - Typography
- `intl` - Internationalization

### **Development Dependencies**
- `build_runner` - Code generation
- `json_serializable` - JSON serialization
- `flutter_lints` - Code linting

## 🚀 Deployment

### **Production Build**
```bash
# Android
flutter build apk --release

# Web
flutter build web --release

# Desktop
flutter build windows --release
flutter build macos --release
flutter build linux --release
```

### **Environment Configuration**
```bash
# Set production environment
export ENVIRONMENT=production
export API_BASE_URL=https://api.foodyeh.io
```

## 🔍 Testing

### **Unit Tests**
```bash
flutter test
```

### **Widget Tests**
```bash
flutter test test/widget_test.dart
```

### **Integration Tests**
```bash
flutter drive --target=test_driver/app.dart
```

## 📊 Performance

### **Optimizations**
- Lazy loading for large lists
- Efficient state management
- Optimized image loading
- Minimal API calls with caching
- Responsive design for all screen sizes

### **Monitoring**
- Real-time system health checks
- API response time monitoring
- Error tracking and logging
- Performance metrics collection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Contact the development team
- Check the documentation

---

**Built with ❤️ using Flutter & Dart**

*Foodyeh Admin Panel - Smart Vending Machine Management* 