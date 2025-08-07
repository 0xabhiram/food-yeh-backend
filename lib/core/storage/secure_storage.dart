import 'dart:convert';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../constants/app_constants.dart';

class SecureStorage {
  static final FlutterSecureStorage _storage = const FlutterSecureStorage(
    aOptions: AndroidOptions(
      encryptedSharedPreferences: true,
    ),
    iOptions: IOSOptions(
      accessibility: KeychainAccessibility.first_unlock_this_device,
    ),
  );

  // Token Management
  static Future<void> saveToken(String token) async {
    await _storage.write(key: AppConstants.tokenKey, value: token);
  }

  static Future<String?> getToken() async {
    return await _storage.read(key: AppConstants.tokenKey);
  }

  static Future<void> deleteToken() async {
    await _storage.delete(key: AppConstants.tokenKey);
  }

  // Refresh Token Management
  static Future<void> saveRefreshToken(String refreshToken) async {
    await _storage.write(key: AppConstants.refreshTokenKey, value: refreshToken);
  }

  static Future<String?> getRefreshToken() async {
    return await _storage.read(key: AppConstants.refreshTokenKey);
  }

  static Future<void> deleteRefreshToken() async {
    await _storage.delete(key: AppConstants.refreshTokenKey);
  }

  // User Data Management
  static Future<void> saveUserData(Map<String, dynamic> userData) async {
    final userJson = jsonEncode(userData);
    await _storage.write(key: AppConstants.userKey, value: userJson);
  }

  static Future<Map<String, dynamic>?> getUserData() async {
    final userJson = await _storage.read(key: AppConstants.userKey);
    if (userJson != null) {
      return jsonDecode(userJson) as Map<String, dynamic>;
    }
    return null;
  }

  static Future<void> deleteUserData() async {
    await _storage.delete(key: AppConstants.userKey);
  }

  // Theme Management
  static Future<void> saveTheme(String theme) async {
    await _storage.write(key: AppConstants.themeKey, value: theme);
  }

  static Future<String?> getTheme() async {
    return await _storage.read(key: AppConstants.themeKey);
  }

  static Future<void> deleteTheme() async {
    await _storage.delete(key: AppConstants.themeKey);
  }

  // Generic Storage Methods
  static Future<void> saveData(String key, String value) async {
    await _storage.write(key: key, value: value);
  }

  static Future<String?> getData(String key) async {
    return await _storage.read(key: key);
  }

  static Future<void> deleteData(String key) async {
    await _storage.delete(key: key);
  }

  static Future<void> deleteAllData() async {
    await _storage.deleteAll();
  }

  // Check if user is logged in
  static Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null && token.isNotEmpty;
  }

  // Clear all authentication data
  static Future<void> clearAuthData() async {
    await deleteToken();
    await deleteRefreshToken();
    await deleteUserData();
  }

  // Get all stored keys
  static Future<List<String>> getAllKeys() async {
    return await _storage.readAll().then((map) => map.keys.toList());
  }

  // Check if key exists
  static Future<bool> hasKey(String key) async {
    return await _storage.containsKey(key: key);
  }
} 