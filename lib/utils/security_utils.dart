import 'dart:convert';
import 'dart:math';

class SecurityUtils {
  // Input sanitization patterns
  static final RegExp _emailPattern = RegExp(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
  );
  
  static final RegExp _usernamePattern = RegExp(
    r'^[a-zA-Z0-9_]{3,20}$',
  );
  
  static final RegExp _phonePattern = RegExp(
    r'^\+?[1-9]\d{1,14}$',
  );
  
  static final RegExp _cardNumberPattern = RegExp(
    r'^\d{4}\s\d{4}\s\d{4}\s\d{4}$',
  );
  
  static final RegExp _cvvPattern = RegExp(
    r'^\d{3,4}$',
  );
  
  static final RegExp _expiryPattern = RegExp(
    r'^(0[1-9]|1[0-2])/([0-9]{2})$',
  );

  // HTML/JS injection patterns
  static final RegExp _htmlPattern = RegExp(
    r'<[^>]*>|javascript:|vbscript:|onload=|onerror=|onclick=',
    caseSensitive: false,
  );
  
  static final RegExp _sqlPattern = RegExp(
    r'(\b(union|select|insert|update|delete|drop|create|alter|exec|execute|script)\b)',
    caseSensitive: false,
  );

  /// Sanitize and validate email
  static String? sanitizeEmail(String? email) {
    if (email == null || email.isEmpty) return null;
    
    // Remove whitespace and convert to lowercase
    String sanitized = email.trim().toLowerCase();
    
    // Check for HTML/JS injection
    if (_htmlPattern.hasMatch(sanitized)) {
      throw SecurityException('Invalid email format');
    }
    
    // Check for SQL injection patterns
    if (_sqlPattern.hasMatch(sanitized)) {
      throw SecurityException('Invalid email format');
    }
    
    // Validate email format
    if (!_emailPattern.hasMatch(sanitized)) {
      throw SecurityException('Invalid email format');
    }
    
    return sanitized;
  }

  /// Sanitize and validate username
  static String? sanitizeUsername(String? username) {
    if (username == null || username.isEmpty) return null;
    
    String sanitized = username.trim();
    
    // Check for HTML/JS injection
    if (_htmlPattern.hasMatch(sanitized)) {
      throw SecurityException('Invalid username format');
    }
    
    // Check for SQL injection patterns
    if (_sqlPattern.hasMatch(sanitized)) {
      throw SecurityException('Invalid username format');
    }
    
    // Validate username format
    if (!_usernamePattern.hasMatch(sanitized)) {
      throw SecurityException('Username must be 3-20 characters, alphanumeric and underscore only');
    }
    
    return sanitized;
  }

  /// Sanitize and validate password
  static String? sanitizePassword(String? password) {
    if (password == null || password.isEmpty) return null;
    
    // Check for HTML/JS injection
    if (_htmlPattern.hasMatch(password)) {
      throw SecurityException('Invalid password format');
    }
    
    // Check for SQL injection patterns
    if (_sqlPattern.hasMatch(password)) {
      throw SecurityException('Invalid password format');
    }
    
    // Password strength validation
    if (password.length < 6) {
      throw SecurityException('Password must be at least 6 characters');
    }
    
    return password;
  }

  /// Sanitize and validate phone number
  static String? sanitizePhone(String? phone) {
    if (phone == null || phone.isEmpty) return null;
    
    // Remove all non-digit characters except +
    String sanitized = phone.replaceAll(RegExp(r'[^\d+]'), '');
    
    // Check for HTML/JS injection
    if (_htmlPattern.hasMatch(phone)) {
      throw SecurityException('Invalid phone format');
    }
    
    // Check for SQL injection patterns
    if (_sqlPattern.hasMatch(phone)) {
      throw SecurityException('Invalid phone format');
    }
    
    // Validate phone format
    if (!_phonePattern.hasMatch(sanitized)) {
      throw SecurityException('Invalid phone number format');
    }
    
    return sanitized;
  }

  /// Sanitize and validate card number
  static String? sanitizeCardNumber(String? cardNumber) {
    if (cardNumber == null || cardNumber.isEmpty) return null;
    
    // Remove all non-digit characters
    String sanitized = cardNumber.replaceAll(RegExp(r'[^\d]'), '');
    
    // Check for HTML/JS injection
    if (_htmlPattern.hasMatch(cardNumber)) {
      throw SecurityException('Invalid card number format');
    }
    
    // Check for SQL injection patterns
    if (_sqlPattern.hasMatch(cardNumber)) {
      throw SecurityException('Invalid card number format');
    }
    
    // Format as XXXX XXXX XXXX XXXX
    if (sanitized.length == 16) {
      sanitized = '${sanitized.substring(0, 4)} ${sanitized.substring(4, 8)} ${sanitized.substring(8, 12)} ${sanitized.substring(12)}';
    }
    
    // Validate card number format
    if (!_cardNumberPattern.hasMatch(sanitized)) {
      throw SecurityException('Invalid card number format');
    }
    
    return sanitized;
  }

  /// Sanitize and validate CVV
  static String? sanitizeCvv(String? cvv) {
    if (cvv == null || cvv.isEmpty) return null;
    
    // Remove all non-digit characters
    String sanitized = cvv.replaceAll(RegExp(r'[^\d]'), '');
    
    // Check for HTML/JS injection
    if (_htmlPattern.hasMatch(cvv)) {
      throw SecurityException('Invalid CVV format');
    }
    
    // Check for SQL injection patterns
    if (_sqlPattern.hasMatch(cvv)) {
      throw SecurityException('Invalid CVV format');
    }
    
    // Validate CVV format
    if (!_cvvPattern.hasMatch(sanitized)) {
      throw SecurityException('CVV must be 3-4 digits');
    }
    
    return sanitized;
  }

  /// Sanitize and validate expiry date
  static String? sanitizeExpiry(String? expiry) {
    if (expiry == null || expiry.isEmpty) return null;
    
    // Check for HTML/JS injection
    if (_htmlPattern.hasMatch(expiry)) {
      throw SecurityException('Invalid expiry date format');
    }
    
    // Check for SQL injection patterns
    if (_sqlPattern.hasMatch(expiry)) {
      throw SecurityException('Invalid expiry date format');
    }
    
    // Validate expiry format
    if (!_expiryPattern.hasMatch(expiry)) {
      throw SecurityException('Expiry date must be in MM/YY format');
    }
    
    // Validate month (01-12)
    String month = expiry.split('/')[0];
    int monthInt = int.tryParse(month) ?? 0;
    if (monthInt < 1 || monthInt > 12) {
      throw SecurityException('Invalid month in expiry date');
    }
    
    return expiry;
  }

  /// Sanitize general text input
  static String? sanitizeText(String? text) {
    if (text == null || text.isEmpty) return null;
    
    String sanitized = text.trim();
    
    // Check for HTML/JS injection
    if (_htmlPattern.hasMatch(sanitized)) {
      throw SecurityException('Invalid text format');
    }
    
    // Check for SQL injection patterns
    if (_sqlPattern.hasMatch(sanitized)) {
      throw SecurityException('Invalid text format');
    }
    
    // Remove any remaining potentially dangerous characters
    sanitized = sanitized.replaceAll(RegExp(r'[<>"\']'), '');
    
    return sanitized;
  }

  /// Generate secure random order ID
  static String generateSecureOrderId() {
    final random = Random.secure();
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    final randomPart = random.nextInt(999999);
    return 'ORD-${timestamp}-${randomPart.toString().padLeft(6, '0')}';
  }

  /// Validate and sanitize order ID
  static String? sanitizeOrderId(String? orderId) {
    if (orderId == null || orderId.isEmpty) return null;
    
    // Check for HTML/JS injection
    if (_htmlPattern.hasMatch(orderId)) {
      throw SecurityException('Invalid order ID format');
    }
    
    // Check for SQL injection patterns
    if (_sqlPattern.hasMatch(orderId)) {
      throw SecurityException('Invalid order ID format');
    }
    
    // Validate order ID format (ORD-XXXXXXXX-XXXXXX)
    if (!RegExp(r'^ORD-\d+-\d{6}$').hasMatch(orderId)) {
      throw SecurityException('Invalid order ID format');
    }
    
    return orderId;
  }

  /// Rate limiting for login attempts
  static final Map<String, int> _loginAttempts = {};
  static final Map<String, DateTime> _lockoutTime = {};
  
  static bool isAccountLocked(String username) {
    final now = DateTime.now();
    final lockoutUntil = _lockoutTime[username];
    
    if (lockoutUntil != null && now.isBefore(lockoutUntil)) {
      return true;
    }
    
    // Clear lockout if expired
    if (lockoutUntil != null && now.isAfter(lockoutUntil)) {
      _lockoutTime.remove(username);
      _loginAttempts[username] = 0;
    }
    
    return false;
  }
  
  static void recordLoginAttempt(String username, bool success) {
    if (success) {
      _loginAttempts[username] = 0;
      _lockoutTime.remove(username);
    } else {
      _loginAttempts[username] = (_loginAttempts[username] ?? 0) + 1;
      
      // Lock account after 5 failed attempts for 15 minutes
      if (_loginAttempts[username]! >= 5) {
        _lockoutTime[username] = DateTime.now().add(const Duration(minutes: 15));
      }
    }
  }

  /// Secure password hashing (in real app, use bcrypt or similar)
  static String hashPassword(String password) {
    // This is a simplified example - in production use proper hashing
    final bytes = utf8.encode(password);
    final hash = base64.encode(bytes);
    return hash;
  }

  /// Validate password strength
  static bool isPasswordStrong(String password) {
    if (password.length < 8) return false;
    
    bool hasUppercase = password.contains(RegExp(r'[A-Z]'));
    bool hasLowercase = password.contains(RegExp(r'[a-z]'));
    bool hasDigits = password.contains(RegExp(r'[0-9]'));
    bool hasSpecialChars = password.contains(RegExp(r'[!@#$%^&*(),.?":{}|<>]'));
    
    return hasUppercase && hasLowercase && hasDigits && hasSpecialChars;
  }
}

/// Custom security exception
class SecurityException implements Exception {
  final String message;
  SecurityException(this.message);
  
  @override
  String toString() => 'SecurityException: $message';
} 