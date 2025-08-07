import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:google_fonts/google_fonts.dart';
import '../models/food_item.dart';
import '../provider/cart_provider.dart';
import '../theme/app_theme.dart';
import 'cart_screen.dart';
import 'login_screen.dart';
import 'profile_screen.dart';
import 'order_history_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final List<FoodItem> foodItems = [
      const FoodItem(id: '1', name: 'Burger', price: 8.99, image: 'burger'),
      const FoodItem(id: '2', name: 'Pizza', price: 12.99, image: 'pizza'),
      const FoodItem(id: '3', name: 'Chicken Wings', price: 9.99, image: 'wings'),
      const FoodItem(id: '4', name: 'French Fries', price: 4.99, image: 'fries'),
      const FoodItem(id: '5', name: 'Hot Dog', price: 6.99, image: 'hotdog'),
      const FoodItem(id: '6', name: 'Sandwich', price: 7.99, image: 'sandwich'),
      const FoodItem(id: '7', name: 'Salad', price: 5.99, image: 'salad'),
      const FoodItem(id: '8', name: 'Ice Cream', price: 3.99, image: 'icecream'),
      const FoodItem(id: '9', name: 'Coffee', price: 2.99, image: 'coffee'),
      const FoodItem(id: '10', name: 'Soda', price: 1.99, image: 'soda'),
      const FoodItem(id: '11', name: 'Cake', price: 4.99, image: 'cake'),
      const FoodItem(id: '12', name: 'Chips', price: 2.49, image: 'chips'),
      const FoodItem(id: '13', name: 'Cookie', price: 1.49, image: 'cookie'),
      const FoodItem(id: '14', name: 'Water', price: 1.00, image: 'water'),
    ];

    return Scaffold(
      appBar: AppBar(
        title: const Text('Foodyeh'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const OrderHistoryScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const ProfileScreen()),
              );
            },
          ),
          IconButton(
            icon: Stack(
              children: [
                const Icon(Icons.shopping_cart),
                Positioned(
                  right: 0,
                  top: 0,
                  child: Consumer<CartProvider>(
                    builder: (context, cart, child) {
                      return cart.itemCount > 0
                          ? Container(
                              padding: const EdgeInsets.all(2),
                              decoration: BoxDecoration(
                                color: AppTheme.accentColor,
                                borderRadius: BorderRadius.circular(10),
                              ),
                              constraints: const BoxConstraints(
                                minWidth: 16,
                                minHeight: 16,
                              ),
                              child: Text(
                                '${cart.itemCount}',
                                style: GoogleFonts.poppins(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                                textAlign: TextAlign.center,
                              ),
                            )
                          : const SizedBox.shrink();
                    },
                  ),
                ),
              ],
            ),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => const CartScreen()),
              );
            },
          ),
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('Logout'),
                  content: const Text('Are you sure you want to logout?'),
                  actions: [
                    TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text('Cancel'),
                    ),
                    ElevatedButton(
                      onPressed: () {
                        Navigator.pop(context);
                        Navigator.pushReplacement(
                          context,
                          MaterialPageRoute(builder: (context) => const LoginScreen()),
                        );
                      },
                      child: const Text('Logout'),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Gradient Header with Glow
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: LinearGradient(
                                 colors: [
                   AppTheme.primaryColor.withValues(alpha: 0.8),
                   AppTheme.accentColor.withValues(alpha: 0.6),
                 ],
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
              ),
                               boxShadow: [
                   BoxShadow(
                     color: AppTheme.primaryColor.withValues(alpha: 0.3),
                     blurRadius: 20,
                     spreadRadius: 5,
                   ),
                 ],
            ),
            child: Column(
              children: [
                Text(
                  'Welcome to Foodyeh',
                  style: GoogleFonts.poppins(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'Choose your favorite food items',
                  style: GoogleFonts.poppins(
                    fontSize: 16,
                    color: Colors.white.withValues(alpha: 0.9),
                  ),
                ),
              ],
            ),
          ),

          // Food Items Grid
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  childAspectRatio: 0.8,
                  crossAxisSpacing: 16,
                  mainAxisSpacing: 16,
                ),
                itemCount: foodItems.length,
                itemBuilder: (context, index) {
                  final item = foodItems[index];
                  return _buildFoodCard(context, item);
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFoodCard(BuildContext context, FoodItem item) {
    return Consumer<CartProvider>(
      builder: (context, cart, child) {
        final quantity = cart.getQuantity(item);
        
        return Card(
          elevation: 8,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          child: Container(
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(16),
              gradient: LinearGradient(
                begin: Alignment.topLeft,
                end: Alignment.bottomRight,
                                 colors: [
                   AppTheme.backgroundColor.withValues(alpha: 0.1),
                   AppTheme.backgroundColor.withValues(alpha: 0.05),
                 ],
              ),
            ),
            child: Column(
              children: [
                // Food Image Placeholder
                Expanded(
                  flex: 3,
                  child: Container(
                    width: double.infinity,
                    margin: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      gradient: LinearGradient(
                                                 colors: [
                           AppTheme.primaryColor.withValues(alpha: 0.3),
                           AppTheme.accentColor.withValues(alpha: 0.3),
                         ],
                      ),
                    ),
                    child: Icon(
                      Icons.restaurant,
                      size: 50,
                      color: AppTheme.primaryColor,
                    ),
                  ),
                ),

                // Food Name
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12),
                  child: Text(
                    item.name,
                    style: GoogleFonts.poppins(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textColor,
                    ),
                    textAlign: TextAlign.center,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),

                // Price
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  child: Text(
                    '\$${item.price.toStringAsFixed(2)}',
                    style: GoogleFonts.poppins(
                      fontSize: 14,
                      fontWeight: FontWeight.w500,
                      color: AppTheme.accentColor,
                    ),
                  ),
                ),

                // Add to Cart Button
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    children: [
                      if (quantity > 0) ...[
                        IconButton(
                          onPressed: () => cart.removeItem(item),
                          icon: const Icon(Icons.remove, color: AppTheme.accentColor),
                                                     style: IconButton.styleFrom(
                             backgroundColor: AppTheme.accentColor.withValues(alpha: 0.1),
                           ),
                        ),
                        Expanded(
                          child: Text(
                            '$quantity',
                            textAlign: TextAlign.center,
                            style: GoogleFonts.poppins(
                              fontWeight: FontWeight.w600,
                              color: AppTheme.textColor,
                            ),
                          ),
                        ),
                      ],
                      Expanded(
                        child: ElevatedButton(
                          onPressed: () {
                            cart.addItem(item);
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text('${item.name} added to cart'),
                                backgroundColor: AppTheme.accentColor,
                                duration: const Duration(seconds: 1),
                              ),
                            );
                          },
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 8),
                          ),
                          child: Text(quantity > 0 ? 'Add More' : 'Add to Cart'),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
} 