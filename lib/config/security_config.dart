class SecurityConfig {
  // Session timeout (in minutes)
  static const int sessionTimeoutMinutes = 30;
  
  // Maximum login attempts before lockout
  static const int maxLoginAttempts = 5;
  
  // Lockout duration (in minutes)
  static const int lockoutDurationMinutes = 15;
  
  // Password minimum length
  static const int minPasswordLength = 8;
  
  // Username minimum length
  static const int minUsernameLength = 3;
  
  // Username maximum length
  static const int maxUsernameLength = 20;
  
  // Card number length
  static const int cardNumberLength = 16;
  
  // CVV minimum length
  static const int minCvvLength = 3;
  
  // CVV maximum length
  static const int maxCvvLength = 4;
  
  // Rate limiting for API calls (requests per minute)
  static const int maxApiRequestsPerMinute = 60;
  
  // Secure headers for HTTP requests
  static const Map<String, String> secureHeaders = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';",
  };
  
  // Allowed file extensions for uploads
  static const List<String> allowedFileExtensions = [
    'jpg', 'jpeg', 'png', 'gif', 'pdf'
  ];
  
  // Maximum file size (in bytes) - 5MB
  static const int maxFileSize = 5 * 1024 * 1024;
  
  // Allowed characters for usernames
  static const String allowedUsernameChars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_';
  
  // Allowed characters for passwords
  static const String allowedPasswordChars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(),.?":{}|<>';
  
  // Minimum password complexity requirements
  static const bool requireUppercase = true;
  static const bool requireLowercase = true;
  static const bool requireNumbers = true;
  static const bool requireSpecialChars = true;
  
  // Session management
  static const bool enableSessionTimeout = true;
  static const bool enableAutoLogout = true;
  
  // Data encryption
  static const bool enableDataEncryption = true;
  static const String encryptionAlgorithm = 'AES-256-GCM';
  
  // Audit logging
  static const bool enableAuditLogging = true;
  static const List<String> auditedEvents = [
    'login',
    'logout',
    'signup',
    'password_change',
    'profile_update',
    'payment',
    'order_creation',
    'order_status_change',
  ];
  
  // Input validation patterns
  static const String emailPattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$';
  static const String phonePattern = r'^\+?[1-9]\d{1,14}$';
  static const String cardNumberPattern = r'^\d{4}\s\d{4}\s\d{4}\s\d{4}$';
  static const String cvvPattern = r'^\d{3,4}$';
  static const String expiryPattern = r'^(0[1-9]|1[0-2])/([0-9]{2})$';
  static const String usernamePattern = r'^[a-zA-Z0-9_]{3,20}$';
  
  // Security headers for API responses
  static Map<String, String> getSecurityHeaders() {
    return Map.from(secureHeaders);
  }
  
  // Validate file upload
  static bool isValidFileUpload(String fileName, int fileSize) {
    if (fileSize > maxFileSize) return false;
    
    String extension = fileName.split('.').last.toLowerCase();
    return allowedFileExtensions.contains(extension);
  }
  
  // Validate username complexity
  static bool isValidUsername(String username) {
    if (username.length < minUsernameLength || username.length > maxUsernameLength) {
      return false;
    }
    
    for (int i = 0; i < username.length; i++) {
      if (!allowedUsernameChars.contains(username[i])) {
        return false;
      }
    }
    
    return true;
  }
  
  // Validate password complexity
  static bool isValidPassword(String password) {
    if (password.length < minPasswordLength) return false;
    
    bool hasUppercase = password.contains(RegExp(r'[A-Z]'));
    bool hasLowercase = password.contains(RegExp(r'[a-z]'));
    bool hasNumbers = password.contains(RegExp(r'[0-9]'));
    bool hasSpecialChars = password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'));
    
    if (requireUppercase && !hasUppercase) return false;
    if (requireLowercase && !hasLowercase) return false;
    if (requireNumbers && !hasNumbers) return false;
    if (requireSpecialChars && !hasSpecialChars) return false;
    
    return true;
  }
} 