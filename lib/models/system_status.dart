import 'package:json_annotation/json_annotation.dart';

part 'system_status.g.dart';

@JsonSerializable()
class HealthCheck {
  final String status;
  final DateTime timestamp;
  final String version;
  final String mqttStatus;
  final String databaseStatus;
  final double uptime;

  HealthCheck({
    required this.status,
    required this.timestamp,
    required this.version,
    required this.mqttStatus,
    required this.databaseStatus,
    required this.uptime,
  });

  factory HealthCheck.fromJson(Map<String, dynamic> json) => _$HealthCheckFromJson(json);
  Map<String, dynamic> toJson() => _$HealthCheckToJson(this);

  bool get isHealthy => status == 'healthy';
  bool get isDegraded => status == 'degraded';
  bool get isUnhealthy => status == 'unhealthy';
}

@JsonSerializable()
class MqttStatus {
  final bool connected;
  final String? broker;
  final int? port;
  final String? clientId;
  final DateTime? lastConnected;
  final DateTime? lastDisconnected;
  final int? messageCount;
  final String? errorMessage;

  MqttStatus({
    required this.connected,
    this.broker,
    this.port,
    this.clientId,
    this.lastConnected,
    this.lastDisconnected,
    this.messageCount,
    this.errorMessage,
  });

  factory MqttStatus.fromJson(Map<String, dynamic> json) => _$MqttStatusFromJson(json);
  Map<String, dynamic> toJson() => _$MqttStatusToJson(this);

  String get statusDisplay {
    return connected ? 'Connected' : 'Disconnected';
  }

  String get statusColor {
    return connected ? '#4CAF50' : '#F44336';
  }
}

@JsonSerializable()
class SystemInfo {
  final String version;
  final DateTime uptime;
  final Map<String, dynamic> mqtt;
  final Map<String, dynamic> database;
  final Map<String, dynamic> rateLimiting;
  final Map<String, dynamic> security;
  final Map<String, dynamic>? hardware;
  final Map<String, dynamic>? network;

  SystemInfo({
    required this.version,
    required this.uptime,
    required this.mqtt,
    required this.database,
    required this.rateLimiting,
    required this.security,
    this.hardware,
    this.network,
  });

  factory SystemInfo.fromJson(Map<String, dynamic> json) => _$SystemInfoFromJson(json);
  Map<String, dynamic> toJson() => _$SystemInfoToJson(this);

  bool get isSystemHealthy {
    return mqtt['status'] == 'healthy' && database['status'] == 'healthy';
  }

  String get systemStatus {
    if (isSystemHealthy) return 'Healthy';
    if (mqtt['status'] == 'unhealthy' || database['status'] == 'unhealthy') {
      return 'Unhealthy';
    }
    return 'Degraded';
  }

  String get systemStatusColor {
    if (isSystemHealthy) return '#4CAF50';
    if (mqtt['status'] == 'unhealthy' || database['status'] == 'unhealthy') {
      return '#F44336';
    }
    return '#FF9800';
  }
}

@JsonSerializable()
class AdminLogEntry {
  final int id;
  final String orderId;
  final String action;
  final String userId;
  final String ipAddress;
  final String details;
  final DateTime createdAt;

  AdminLogEntry({
    required this.id,
    required this.orderId,
    required this.action,
    required this.userId,
    required this.ipAddress,
    required this.details,
    required this.createdAt,
  });

  factory AdminLogEntry.fromJson(Map<String, dynamic> json) => _$AdminLogEntryFromJson(json);
  Map<String, dynamic> toJson() => _$AdminLogEntryToJson(this);

  String get actionDisplay {
    switch (action.toLowerCase()) {
      case 'order_created':
        return 'Order Created';
      case 'status_update':
        return 'Status Updated';
      case 'mqtt_message':
        return 'MQTT Message';
      case 'reboot_device':
        return 'Device Reboot';
      case 'override_command':
        return 'Override Command';
      case 'clear_rate_limits':
        return 'Clear Rate Limits';
      default:
        return action;
    }
  }

  String get actionColor {
    switch (action.toLowerCase()) {
      case 'order_created':
        return '#4CAF50';
      case 'status_update':
        return '#2196F3';
      case 'mqtt_message':
        return '#FF9800';
      case 'reboot_device':
        return '#F44336';
      case 'override_command':
        return '#9C27B0';
      case 'clear_rate_limits':
        return '#FF5722';
      default:
        return '#757575';
    }
  }
}

@JsonSerializable()
class AdminLogsResponse {
  final List<AdminLogEntry> logs;
  final int total;
  final int page;
  final int perPage;

  AdminLogsResponse({
    required this.logs,
    required this.total,
    required this.page,
    required this.perPage,
  });

  factory AdminLogsResponse.fromJson(Map<String, dynamic> json) => _$AdminLogsResponseFromJson(json);
  Map<String, dynamic> toJson() => _$AdminLogsResponseToJson(this);
}

@JsonSerializable()
class AuditTrailEntry {
  final int id;
  final String userId;
  final String action;
  final String resource;
  final String resourceId;
  final String ipAddress;
  final String userAgent;
  final Map<String, dynamic>? changes;
  final DateTime createdAt;

  AuditTrailEntry({
    required this.id,
    required this.userId,
    required this.action,
    required this.resource,
    required this.resourceId,
    required this.ipAddress,
    required this.userAgent,
    this.changes,
    required this.createdAt,
  });

  factory AuditTrailEntry.fromJson(Map<String, dynamic> json) => _$AuditTrailEntryFromJson(json);
  Map<String, dynamic> toJson() => _$AuditTrailEntryToJson(this);

  String get actionDisplay {
    switch (action.toLowerCase()) {
      case 'create':
        return 'Created';
      case 'update':
        return 'Updated';
      case 'delete':
        return 'Deleted';
      case 'login':
        return 'Login';
      case 'logout':
        return 'Logout';
      case 'reboot':
        return 'Reboot';
      case 'override':
        return 'Override';
      default:
        return action;
    }
  }

  String get actionColor {
    switch (action.toLowerCase()) {
      case 'create':
        return '#4CAF50';
      case 'update':
        return '#2196F3';
      case 'delete':
        return '#F44336';
      case 'login':
        return '#4CAF50';
      case 'logout':
        return '#FF9800';
      case 'reboot':
        return '#F44336';
      case 'override':
        return '#9C27B0';
      default:
        return '#757575';
    }
  }
}

@JsonSerializable()
class AuditTrailResponse {
  final List<AuditTrailEntry> entries;
  final int total;
  final int page;
  final int perPage;

  AuditTrailResponse({
    required this.entries,
    required this.total,
    required this.page,
    required this.perPage,
  });

  factory AuditTrailResponse.fromJson(Map<String, dynamic> json) => _$AuditTrailResponseFromJson(json);
  Map<String, dynamic> toJson() => _$AuditTrailResponseToJson(this);
} 