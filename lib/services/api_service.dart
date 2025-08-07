import 'dart:convert';
import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import '../core/constants/app_constants.dart';
import '../core/storage/secure_storage.dart';
import '../models/user.dart';
import '../models/order.dart';
import '../models/food_item.dart';
import '../models/system_status.dart';

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  late Dio _dio;
  String? _token;

  void initialize() {
    _dio = Dio(BaseOptions(
      baseUrl: '${AppConstants.baseUrl}${AppConstants.apiVersion}',
      connectTimeout: Duration(milliseconds: AppConstants.connectionTimeout),
      receiveTimeout: Duration(milliseconds: AppConstants.receiveTimeout),
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    ));

    _setupInterceptors();
  }

  void _setupInterceptors() {
    // Request interceptor for adding auth token
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        if (_token != null) {
          options.headers['Authorization'] = 'Bearer $_token';
        }
        handler.next(options);
      },
      onError: (error, handler) async {
        if (error.response?.statusCode == 401) {
          // Token expired, try to refresh
          final refreshed = await _refreshToken();
          if (refreshed) {
            // Retry the original request
            final response = await _dio.request(
              error.requestOptions.path,
              options: Options(
                method: error.requestOptions.method,
                headers: error.requestOptions.headers,
              ),
              data: error.requestOptions.data,
              queryParameters: error.requestOptions.queryParameters,
            );
            handler.resolve(response);
            return;
          }
        }
        handler.next(error);
      },
    ));

    // Response interceptor for logging
    _dio.interceptors.add(LogInterceptor(
      requestBody: kDebugMode,
      responseBody: kDebugMode,
      logPrint: (obj) {
        if (kDebugMode) {
          print(obj);
        }
      },
    ));
  }

  Future<void> setToken(String token) async {
    _token = token;
    await SecureStorage.saveToken(token);
  }

  Future<void> clearToken() async {
    _token = null;
    await SecureStorage.deleteToken();
  }

  Future<bool> _refreshToken() async {
    try {
      final refreshToken = await SecureStorage.getRefreshToken();
      if (refreshToken == null) return false;

      final response = await _dio.post('/auth/refresh', data: {
        'refresh_token': refreshToken,
      });

      if (response.statusCode == 200) {
        final newToken = response.data['access_token'];
        await setToken(newToken);
        return true;
      }
    } catch (e) {
      if (kDebugMode) {
        print('Token refresh failed: $e');
      }
    }
    return false;
  }

  // Authentication
  Future<Map<String, dynamic>> login(String username, String password) async {
    try {
      final response = await _dio.post(AppConstants.loginEndpoint, data: {
        'username': username,
        'password': password,
      });

      if (response.statusCode == 200) {
        final data = response.data;
        await setToken(data['access_token']);
        if (data['refresh_token'] != null) {
          await SecureStorage.saveRefreshToken(data['refresh_token']);
        }
        return data;
      }
      throw Exception('Login failed');
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<void> logout() async {
    try {
      await _dio.post('/auth/logout');
    } catch (e) {
      // Ignore logout errors
    } finally {
      await SecureStorage.clearAuthData();
      _token = null;
    }
  }

  // Health and Status
  Future<HealthCheck> getHealthStatus() async {
    try {
      final response = await _dio.get(AppConstants.healthEndpoint);
      return HealthCheck.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<MqttStatus> getMqttStatus() async {
    try {
      final response = await _dio.get(AppConstants.mqttStatusEndpoint);
      return MqttStatus.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<SystemInfo> getSystemInfo() async {
    try {
      final response = await _dio.get(AppConstants.systemInfoEndpoint);
      return SystemInfo.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // Orders
  Future<OrderListResponse> getOrders({
    int page = 1,
    int perPage = 20,
    String? status,
    String? orderId,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'per_page': perPage,
      };
      if (status != null) queryParams['status'] = status;
      if (orderId != null) queryParams['order_id'] = orderId;

      final response = await _dio.get('/order', queryParameters: queryParams);
      return OrderListResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<Order> getOrder(String orderId) async {
    try {
      final response = await _dio.get('/order/$orderId');
      return Order.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<Order> updateOrderStatus(String orderId, String status) async {
    try {
      final response = await _dio.put('/order/$orderId/status', data: {
        'status': status,
      });
      return Order.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<void> cancelOrder(String orderId) async {
    try {
      await _dio.delete('/order/$orderId');
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // Food Items
  Future<FoodItemListResponse> getFoodItems({
    int page = 1,
    int perPage = 20,
    String? category,
    bool? isAvailable,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'per_page': perPage,
      };
      if (category != null) queryParams['category'] = category;
      if (isAvailable != null) queryParams['is_available'] = isAvailable;

      final response = await _dio.get('/items', queryParameters: queryParams);
      return FoodItemListResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<FoodItem> getFoodItem(String itemId) async {
    try {
      final response = await _dio.get('/items/$itemId');
      return FoodItem.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<FoodItem> createFoodItem(CreateFoodItemRequest request) async {
    try {
      final response = await _dio.post('/items', data: request.toJson());
      return FoodItem.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<FoodItem> updateFoodItem(String itemId, UpdateFoodItemRequest request) async {
    try {
      final response = await _dio.put('/items/$itemId', data: request.toJson());
      return FoodItem.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<void> deleteFoodItem(String itemId) async {
    try {
      await _dio.delete('/items/$itemId');
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // Admin Logs
  Future<AdminLogsResponse> getAdminLogs({
    int page = 1,
    int perPage = 50,
    String? action,
    String? userId,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'per_page': perPage,
      };
      if (action != null) queryParams['action'] = action;
      if (userId != null) queryParams['user_id'] = userId;

      final response = await _dio.get(AppConstants.logsEndpoint, queryParameters: queryParams);
      return AdminLogsResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<AuditTrailResponse> getAuditTrail({
    int page = 1,
    int perPage = 50,
    String? action,
    String? userId,
    String? resource,
    String? startDate,
    String? endDate,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'per_page': perPage,
      };
      if (action != null) queryParams['action'] = action;
      if (userId != null) queryParams['user_id'] = userId;
      if (resource != null) queryParams['resource'] = resource;
      if (startDate != null) queryParams['start_date'] = startDate;
      if (endDate != null) queryParams['end_date'] = endDate;

      final response = await _dio.get(AppConstants.auditTrailEndpoint, queryParameters: queryParams);
      return AuditTrailResponse.fromJson(response.data);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // Admin Controls
  Future<void> rebootDevice() async {
    try {
      await _dio.post(AppConstants.rebootEndpoint);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<void> overrideCommand(Map<String, dynamic> command) async {
    try {
      await _dio.post(AppConstants.overrideEndpoint, data: command);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  Future<void> clearRateLimits(String identifier, {String limitType = 'ip'}) async {
    try {
      await _dio.post(AppConstants.clearRateLimitsEndpoint, data: {
        'identifier': identifier,
        'limit_type': limitType,
      });
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  // Error handling
  Exception _handleDioError(DioException error) {
    switch (error.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.sendTimeout:
      case DioExceptionType.receiveTimeout:
        return Exception(AppConstants.networkErrorMessage);
      case DioExceptionType.badResponse:
        final statusCode = error.response?.statusCode;
        final message = error.response?.data?['detail'] ?? 'Request failed';
        
        switch (statusCode) {
          case 401:
            return Exception(AppConstants.unauthorizedMessage);
          case 403:
            return Exception(AppConstants.forbiddenMessage);
          case 422:
            return Exception('Validation error: $message');
          case 500:
            return Exception('Server error: $message');
          default:
            return Exception(message);
        }
      case DioExceptionType.cancel:
        return Exception('Request cancelled');
      default:
        return Exception(AppConstants.networkErrorMessage);
    }
  }
} 