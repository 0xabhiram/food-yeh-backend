import 'package:flutter/foundation.dart';
import '../core/storage/secure_storage.dart';
import '../models/user.dart';
import 'api_service.dart';

class AuthService extends ChangeNotifier {
  static final AuthService _instance = AuthService._internal();
  factory AuthService() => _instance;
  AuthService._internal();

  User? _currentUser;
  bool _isLoading = false;
  String? _error;

  User? get currentUser => _currentUser;
  bool get isLoading => _isLoading;
  String? get error => _error;
  bool get isLoggedIn => _currentUser != null;

  // Initialize auth service
  Future<void> initialize() async {
    _isLoading = true;
    notifyListeners();

    try {
      final token = await SecureStorage.getToken();
      if (token != null) {
        // Try to get user data from storage
        final userData = await SecureStorage.getUserData();
        if (userData != null) {
          _currentUser = User.fromJson(userData);
        }
      }
    } catch (e) {
      if (kDebugMode) {
        print('Auth initialization error: $e');
      }
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Login
  Future<bool> login(String username, String password) async {
    _isLoading = true;
    _error = null;
    notifyListeners();

    try {
      final response = await ApiService().login(username, password);
      
      if (response['user'] != null) {
        _currentUser = User.fromJson(response['user']);
        await SecureStorage.saveUserData(response['user']);
        _error = null;
        notifyListeners();
        return true;
      } else {
        _error = 'Invalid response from server';
        notifyListeners();
        return false;
      }
    } catch (e) {
      _error = e.toString();
      notifyListeners();
      return false;
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // Logout
  Future<void> logout() async {
    _isLoading = true;
    notifyListeners();

    try {
      await ApiService().logout();
    } catch (e) {
      if (kDebugMode) {
        print('Logout error: $e');
      }
    } finally {
      _currentUser = null;
      _error = null;
      _isLoading = false;
      notifyListeners();
    }
  }

  // Check if user has permission
  bool hasPermission(String permission) {
    return _currentUser?.hasPermission(permission) ?? false;
  }

  bool hasAnyPermission(List<String> permissions) {
    return _currentUser?.hasAnyPermission(permissions) ?? false;
  }

  bool hasAllPermissions(List<String> permissions) {
    return _currentUser?.hasAllPermissions(permissions) ?? false;
  }

  // Check if user is admin
  bool get isAdmin => _currentUser?.isAdmin ?? false;
  bool get isSuperAdmin => _currentUser?.isSuperAdmin ?? false;

  // Update user data
  void updateUser(User user) {
    _currentUser = user;
    notifyListeners();
  }

  // Clear error
  void clearError() {
    _error = null;
    notifyListeners();
  }

  // Get user display name
  String get userDisplayName {
    return _currentUser?.displayName ?? 'Unknown User';
  }

  // Get user role
  String get userRole {
    return _currentUser?.role ?? 'user';
  }

  // Check if user can perform admin actions
  bool canPerformAdminAction(String action) {
    if (!isAdmin) return false;
    
    switch (action) {
      case 'reboot_device':
        return hasPermission('admin:reboot');
      case 'override_commands':
        return hasPermission('admin:override');
      case 'clear_rate_limits':
        return hasPermission('admin:rate_limits');
      case 'view_logs':
        return hasPermission('admin:logs');
      case 'view_audit_trail':
        return hasPermission('admin:audit');
      case 'manage_items':
        return hasPermission('admin:items');
      case 'manage_orders':
        return hasPermission('admin:orders');
      default:
        return false;
    }
  }

  // Get user permissions list
  List<String> get userPermissions {
    return _currentUser?.permissions ?? [];
  }

  // Check if user is active
  bool get isUserActive {
    return _currentUser?.isActive ?? false;
  }

  // Get user creation date
  DateTime? get userCreatedAt {
    return _currentUser?.createdAt;
  }

  // Get user last login
  DateTime? get userLastLogin {
    return _currentUser?.lastLoginAt;
  }

  // Format user info for display
  Map<String, String> get userInfo {
    if (_currentUser == null) {
      return {
        'name': 'Not logged in',
        'role': 'Guest',
        'email': 'N/A',
        'status': 'Inactive',
      };
    }

    return {
      'name': _currentUser!.displayName,
      'role': _currentUser!.role,
      'email': _currentUser!.email,
      'status': _currentUser!.isActive ? 'Active' : 'Inactive',
    };
  }

  // Get user avatar
  String? get userAvatar {
    return _currentUser?.avatar;
  }

  // Check if user can access specific features
  bool canAccessFeature(String feature) {
    switch (feature) {
      case 'dashboard':
        return isLoggedIn;
      case 'orders':
        return hasPermission('view:orders') || isAdmin;
      case 'items':
        return hasPermission('manage:items') || isAdmin;
      case 'logs':
        return hasPermission('view:logs') || isAdmin;
      case 'audit':
        return hasPermission('view:audit') || isAdmin;
      case 'controls':
        return hasPermission('admin:controls') || isSuperAdmin;
      case 'system':
        return hasPermission('view:system') || isAdmin;
      default:
        return false;
    }
  }

  // Get accessible features for current user
  List<String> get accessibleFeatures {
    final features = <String>[];
    
    if (canAccessFeature('dashboard')) features.add('dashboard');
    if (canAccessFeature('orders')) features.add('orders');
    if (canAccessFeature('items')) features.add('items');
    if (canAccessFeature('logs')) features.add('logs');
    if (canAccessFeature('audit')) features.add('audit');
    if (canAccessFeature('controls')) features.add('controls');
    if (canAccessFeature('system')) features.add('system');
    
    return features;
  }

  // Validate session
  Future<bool> validateSession() async {
    try {
      final token = await SecureStorage.getToken();
      if (token == null) return false;

      // Try to get user data to validate session
      final userData = await SecureStorage.getUserData();
      if (userData == null) return false;

      _currentUser = User.fromJson(userData);
      notifyListeners();
      return true;
    } catch (e) {
      if (kDebugMode) {
        print('Session validation error: $e');
      }
      return false;
    }
  }

  // Refresh user data
  Future<void> refreshUserData() async {
    try {
      final userData = await SecureStorage.getUserData();
      if (userData != null) {
        _currentUser = User.fromJson(userData);
        notifyListeners();
      }
    } catch (e) {
      if (kDebugMode) {
        print('Refresh user data error: $e');
      }
    }
  }
} 