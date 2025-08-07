class AppConstants {
  // API Configuration
  static const String baseUrl = 'https://api.foodyeh.io';
  static const String apiVersion = '/api/v1';
  
  // API Endpoints
  static const String loginEndpoint = '/auth/login';
  static const String healthEndpoint = '/status/health';
  static const String mqttStatusEndpoint = '/status/mqtt';
  static const String systemInfoEndpoint = '/admin/system-info';
  static const String logsEndpoint = '/admin/logs';
  static const String auditTrailEndpoint = '/admin/audit-trail';
  static const String rebootEndpoint = '/admin/reboot';
  static const String overrideEndpoint = '/admin/override';
  static const String clearRateLimitsEndpoint = '/admin/clear-rate-limits';
  
  // Storage Keys
  static const String tokenKey = 'auth_token';
  static const String refreshTokenKey = 'refresh_token';
  static const String userKey = 'user_data';
  static const String themeKey = 'app_theme';
  
  // App Configuration
  static const String appName = 'Foodyeh Admin';
  static const String appVersion = '1.0.0';
  
  // Timeouts
  static const int connectionTimeout = 30000; // 30 seconds
  static const int receiveTimeout = 30000; // 30 seconds
  
  // Pagination
  static const int defaultPageSize = 20;
  static const int maxPageSize = 100;
  
  // Status Messages
  static const String successMessage = 'Operation completed successfully';
  static const String errorMessage = 'An error occurred';
  static const String networkErrorMessage = 'Network error. Please check your connection.';
  static const String unauthorizedMessage = 'Unauthorized. Please login again.';
  static const String forbiddenMessage = 'Access denied. Insufficient permissions.';
  
  // Validation Messages
  static const String requiredFieldMessage = 'This field is required';
  static const String invalidEmailMessage = 'Please enter a valid email address';
  static const String invalidPasswordMessage = 'Password must be at least 6 characters';
  static const String passwordMismatchMessage = 'Passwords do not match';
  
  // Order Status
  static const String statusPending = 'pending';
  static const String statusProcessing = 'processing';
  static const String statusCompleted = 'completed';
  static const String statusCancelled = 'cancelled';
  static const String statusFailed = 'failed';
  
  // System Status
  static const String statusOnline = 'online';
  static const String statusOffline = 'offline';
  static const String statusWarning = 'warning';
  static const String statusError = 'error';
  
  // Date Formats
  static const String dateFormat = 'yyyy-MM-dd';
  static const String timeFormat = 'HH:mm:ss';
  static const String dateTimeFormat = 'yyyy-MM-dd HH:mm:ss';
  static const String displayDateFormat = 'MMM dd, yyyy';
  static const String displayTimeFormat = 'hh:mm a';
  
  // Animation Durations
  static const Duration shortAnimation = Duration(milliseconds: 200);
  static const Duration mediumAnimation = Duration(milliseconds: 300);
  static const Duration longAnimation = Duration(milliseconds: 500);
  
  // Refresh Intervals
  static const Duration dashboardRefreshInterval = Duration(seconds: 30);
  static const Duration statusRefreshInterval = Duration(seconds: 10);
  static const Duration logsRefreshInterval = Duration(minutes: 1);
  
  // Error Codes
  static const int networkErrorCode = 1001;
  static const int unauthorizedErrorCode = 1002;
  static const int forbiddenErrorCode = 1003;
  static const int validationErrorCode = 1004;
  static const int serverErrorCode = 1005;
  
  // Success Codes
  static const int successCode = 200;
  static const int createdCode = 201;
  static const int noContentCode = 204;
} 