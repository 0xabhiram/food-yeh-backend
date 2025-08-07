import 'package:json_annotation/json_annotation.dart';

part 'food_item.g.dart';

@JsonSerializable()
class FoodItem {
  final String id;
  final String name;
  final String description;
  final double price;
  final int slotId;
  final String imageUrl;
  final bool isAvailable;
  final int stockQuantity;
  final String category;
  final List<String> tags;
  final Map<String, dynamic>? nutritionalInfo;
  final DateTime createdAt;
  final DateTime updatedAt;
  final String? createdBy;
  final String? updatedBy;

  FoodItem({
    required this.id,
    required this.name,
    required this.description,
    required this.price,
    required this.slotId,
    required this.imageUrl,
    required this.isAvailable,
    required this.stockQuantity,
    required this.category,
    required this.tags,
    this.nutritionalInfo,
    required this.createdAt,
    required this.updatedAt,
    this.createdBy,
    this.updatedBy,
  });

  factory FoodItem.fromJson(Map<String, dynamic> json) => _$FoodItemFromJson(json);
  Map<String, dynamic> toJson() => _$FoodItemToJson(this);

  bool get isOutOfStock => stockQuantity <= 0;
  bool get isLowStock => stockQuantity <= 5 && stockQuantity > 0;
  bool get isInStock => stockQuantity > 5;

  String get stockStatus {
    if (isOutOfStock) return 'Out of Stock';
    if (isLowStock) return 'Low Stock';
    return 'In Stock';
  }

  String get stockStatusColor {
    if (isOutOfStock) return '#F44336'; // Red
    if (isLowStock) return '#FF9800'; // Orange
    return '#4CAF50'; // Green
  }

  String get formattedPrice {
    return '\$${price.toStringAsFixed(2)}';
  }

  String get displayName {
    return '$name (Slot $slotId)';
  }

  FoodItem copyWith({
    String? id,
    String? name,
    String? description,
    double? price,
    int? slotId,
    String? imageUrl,
    bool? isAvailable,
    int? stockQuantity,
    String? category,
    List<String>? tags,
    Map<String, dynamic>? nutritionalInfo,
    DateTime? createdAt,
    DateTime? updatedAt,
    String? createdBy,
    String? updatedBy,
  }) {
    return FoodItem(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      price: price ?? this.price,
      slotId: slotId ?? this.slotId,
      imageUrl: imageUrl ?? this.imageUrl,
      isAvailable: isAvailable ?? this.isAvailable,
      stockQuantity: stockQuantity ?? this.stockQuantity,
      category: category ?? this.category,
      tags: tags ?? this.tags,
      nutritionalInfo: nutritionalInfo ?? this.nutritionalInfo,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      createdBy: createdBy ?? this.createdBy,
      updatedBy: updatedBy ?? this.updatedBy,
    );
  }

  @override
  String toString() {
    return 'FoodItem(id: $id, name: $name, slotId: $slotId, price: $price, stockQuantity: $stockQuantity)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is FoodItem && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
}

@JsonSerializable()
class FoodItemListResponse {
  final List<FoodItem> items;
  final int total;
  final int page;
  final int perPage;
  final int totalPages;

  FoodItemListResponse({
    required this.items,
    required this.total,
    required this.page,
    required this.perPage,
    required this.totalPages,
  });

  factory FoodItemListResponse.fromJson(Map<String, dynamic> json) => _$FoodItemListResponseFromJson(json);
  Map<String, dynamic> toJson() => _$FoodItemListResponseToJson(this);
}

@JsonSerializable()
class CreateFoodItemRequest {
  final String name;
  final String description;
  final double price;
  final int slotId;
  final String imageUrl;
  final String category;
  final List<String> tags;
  final Map<String, dynamic>? nutritionalInfo;

  CreateFoodItemRequest({
    required this.name,
    required this.description,
    required this.price,
    required this.slotId,
    required this.imageUrl,
    required this.category,
    required this.tags,
    this.nutritionalInfo,
  });

  factory CreateFoodItemRequest.fromJson(Map<String, dynamic> json) => _$CreateFoodItemRequestFromJson(json);
  Map<String, dynamic> toJson() => _$CreateFoodItemRequestToJson(this);
}

@JsonSerializable()
class UpdateFoodItemRequest {
  final String? name;
  final String? description;
  final double? price;
  final int? slotId;
  final String? imageUrl;
  final bool? isAvailable;
  final int? stockQuantity;
  final String? category;
  final List<String>? tags;
  final Map<String, dynamic>? nutritionalInfo;

  UpdateFoodItemRequest({
    this.name,
    this.description,
    this.price,
    this.slotId,
    this.imageUrl,
    this.isAvailable,
    this.stockQuantity,
    this.category,
    this.tags,
    this.nutritionalInfo,
  });

  factory UpdateFoodItemRequest.fromJson(Map<String, dynamic> json) => _$UpdateFoodItemRequestFromJson(json);
  Map<String, dynamic> toJson() => _$UpdateFoodItemRequestToJson(this);
} 