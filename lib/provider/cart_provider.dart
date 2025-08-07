import 'package:flutter/foundation.dart';
import '../models/food_item.dart';

class CartProvider with ChangeNotifier {
  final Map<FoodItem, int> _items = {};

  Map<FoodItem, int> get items => {..._items};

  int get itemCount => _items.length;

  double get totalPrice {
    double total = 0.0;
    _items.forEach((item, quantity) {
      total += item.price * quantity;
    });
    return total;
  }

  void addItem(FoodItem foodItem) {
    if (_items.containsKey(foodItem)) {
      _items[foodItem] = (_items[foodItem] ?? 0) + 1;
    } else {
      _items[foodItem] = 1;
    }
    notifyListeners();
  }

  void removeItem(FoodItem foodItem) {
    if (_items.containsKey(foodItem)) {
      if (_items[foodItem]! > 1) {
        _items[foodItem] = _items[foodItem]! - 1;
      } else {
        _items.remove(foodItem);
      }
    }
    notifyListeners();
  }

  void clearCart() {
    _items.clear();
    notifyListeners();
  }

  int getQuantity(FoodItem foodItem) {
    return _items[foodItem] ?? 0;
  }
} 