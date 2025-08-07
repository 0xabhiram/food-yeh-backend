import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String id;
  final String username;
  final String email;
  final String role;
  final String? firstName;
  final String? lastName;
  final String? avatar;
  final DateTime createdAt;
  final DateTime? lastLoginAt;
  final bool isActive;
  final List<String> permissions;

  User({
    required this.id,
    required this.username,
    required this.email,
    required this.role,
    this.firstName,
    this.lastName,
    this.avatar,
    required this.createdAt,
    this.lastLoginAt,
    required this.isActive,
    required this.permissions,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);

  String get fullName {
    if (firstName != null && lastName != null) {
      return '$firstName $lastName';
    } else if (firstName != null) {
      return firstName!;
    } else if (lastName != null) {
      return lastName!;
    }
    return username;
  }

  String get displayName {
    return fullName.isNotEmpty ? fullName : username;
  }

  bool get isAdmin => role.toLowerCase() == 'admin';
  bool get isSuperAdmin => role.toLowerCase() == 'super_admin';

  bool hasPermission(String permission) {
    return permissions.contains(permission) || isAdmin;
  }

  bool hasAnyPermission(List<String> requiredPermissions) {
    return requiredPermissions.any((permission) => hasPermission(permission));
  }

  bool hasAllPermissions(List<String> requiredPermissions) {
    return requiredPermissions.every((permission) => hasPermission(permission));
  }

  User copyWith({
    String? id,
    String? username,
    String? email,
    String? role,
    String? firstName,
    String? lastName,
    String? avatar,
    DateTime? createdAt,
    DateTime? lastLoginAt,
    bool? isActive,
    List<String>? permissions,
  }) {
    return User(
      id: id ?? this.id,
      username: username ?? this.username,
      email: email ?? this.email,
      role: role ?? this.role,
      firstName: firstName ?? this.firstName,
      lastName: lastName ?? this.lastName,
      avatar: avatar ?? this.avatar,
      createdAt: createdAt ?? this.createdAt,
      lastLoginAt: lastLoginAt ?? this.lastLoginAt,
      isActive: isActive ?? this.isActive,
      permissions: permissions ?? this.permissions,
    );
  }

  @override
  String toString() {
    return 'User(id: $id, username: $username, email: $email, role: $role, isActive: $isActive)';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is User && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;
} 