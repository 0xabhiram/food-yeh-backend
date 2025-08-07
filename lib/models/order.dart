import 'package:json_annotation/json_annotation.dart';

part 'order.g.dart';

@JsonSerializable()
class Order {
  final String orderId;
  final String itemId;
  final String itemName;
  final int slotId;
  final int quantity;
  final double price;
  final double totalAmount;
  final String status;
  final String orderType;
  final String? userId;
  final String? userName;
  final String? ipAddress;
  final DateTime createdAt;
  final DateTime updatedAt;
  final DateTime? completedAt;
  final String? errorMessage;
  final Map<String, dynamic>? metadata;

  Order({
    required this.orderId,
    required this.itemId,
    required this.itemName,
    required this.slotId,
    required this.quantity,
    required this.price,
    required this.totalAmount,
    required this.status,
    required this.orderType,
    this.userId,
    this.userName,
    this.ipAddress,
    required this.createdAt,
    required this.updatedAt,
    this.completedAt,
    this.errorMessage,
    this.metadata,
  });

  factory Order.fromJson(Map<String, dynamic> json) => _$OrderFromJson(json);
  Map<String, dynamic> toJson() => _$OrderToJson(this);

  bool get isPending => status == 'pending';
  bool get isProcessing => status == 'processing';
  bool get isCompleted => status == 'completed';
  bool get isCancelled => status == 'cancelled';
  bool get isFailed => status == 'failed';

  String get statusDisplay {
    switch (status.toLowerCase()) {
      case 'pending':
        return 'Pending';
      case 'processing':
        return 'Processing';
      case 'completed':
        return 'Completed';
      case 'cancelled':
        return 'Cancelled';
      case 'failed':
        return 'Failed';
      default:
        return status;
    }
  }

  String get statusColor {
    switch (status.toLowerCase()) {
      case 'pending':
        return '#FF9800'; // Orange
      case 'processing':
        return '#2196F3'; // Blue
      case 'completed':
        return '#4CAF50'; // Green
      case 'cancelled':
        return '#F44336'; // Red
      case 'failed':
        return '#F44336'; // Red
      default:
        return '#757575'; // Grey
    }
  }

  Duration get processingTime {
    if (completedAt != null) {
      return completedAt!.difference(createdAt);
    }
    return DateTime.now().difference(createdAt);
  }

  String get processingTimeDisplay {
    final duration = processingTime;
    if (duration.inMinutes < 1) {
      return '${duration.inSeconds}s';
    } else if (duration.inHours < 1) {
      return '${duration.inMinutes}m ${duration.inSeconds % 60}s';
    } else {
      return '${duration.inHours}h ${duration.inMinutes % 60}m';
    }
  }

  Order copyWith({
    String? orderId,
    String? itemId,
    String? itemName,
    int? slotId,
    int? quantity,
    double? price,
    double? totalAmount,
    String? status,
    String? orderType,
    String? userId,
    String? userName,
    String? ipAddress,
    DateTime? createdAt,
    DateTime? updatedAt,
    DateTime? completedAt,
    String? errorMessage,
    Map<String, dynamic>? metadata,
  }) {
    return Order(
      orderId: orderId ?? this.orderId,
      itemId: itemId ?? this.itemId,
      itemName: itemName ?? this.itemName,
      slotId: slotId ?? this.slotId,
      quantity: quantity ?? this.quantity,
      price: price ?? this.price,
      totalAmount: totalAmount ?? this.totalAmount,
      status: status ?? this.status,
      orderType: orderType ?? this.orderType,
      userId: userId ?? this.userId,
      userName: userName ?? this.userName,
      ipAddress: ipAddress ?? this.ipAddress,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      completedAt: completedAt ?? this.completedAt,
      errorMessage: errorMessage ?? this.errorMessage,
      metadata: metadata ?? this.metadata,
    );
  }

  @override
  String toString() {
    return 'Order(orderId: $orderId, itemName: $itemName, status: $status, totalAmount: $totalAmount)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Order && other.orderId == orderId;
  }

  @override
  int get hashCode => orderId.hashCode;
}

@JsonSerializable()
class OrderListResponse {
  final List<Order> orders;
  final int total;
  final int page;
  final int perPage;
  final int totalPages;

  OrderListResponse({
    required this.orders,
    required this.total,
    required this.page,
    required this.perPage,
    required this.totalPages,
  });

  factory OrderListResponse.fromJson(Map<String, dynamic> json) => _$OrderListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$OrderListResponseToJson(this);
} 