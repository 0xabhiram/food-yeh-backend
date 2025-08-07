import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../utils/security_utils.dart';

class OrderStatusScreen extends StatefulWidget {
  const OrderStatusScreen({super.key});

  @override
  State<OrderStatusScreen> createState() => _OrderStatusScreenState();
}

class _OrderStatusScreenState extends State<OrderStatusScreen> {
  // Mock order data
  final String orderId = SecurityUtils.generateSecureOrderId();
  final String currentStatus = 'Cooking';
  final String estimatedTime = '15 minutes';
  final int currentStep = 2; // 0: Ordered, 1: Confirmed, 2: Cooking, 3: Packing, 4: Ready

  final List<Map<String, dynamic>> stages = [
    {'name': 'Ordered', 'icon': Icons.shopping_cart, 'completed': true},
    {'name': 'Confirmed', 'icon': Icons.check_circle, 'completed': true},
    {'name': 'Cooking', 'icon': Icons.restaurant, 'completed': false, 'current': true},
    {'name': 'Packing', 'icon': Icons.inventory, 'completed': false},
    {'name': 'Ready', 'icon': Icons.done_all, 'completed': false},
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Order Status'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Order Header
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
                borderRadius: BorderRadius.circular(16),
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
                  Icon(
                    Icons.track_changes,
                    size: 60,
                    color: Colors.white,
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'Order Status',
                    style: GoogleFonts.poppins(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Track your order progress',
                    style: GoogleFonts.poppins(
                      fontSize: 16,
                      color: Colors.white.withValues(alpha: 0.9),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Order Details Card
            Card(
              elevation: 4,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
              child: Container(
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [
                      AppTheme.backgroundColor.withValues(alpha: 0.1),
                      AppTheme.backgroundColor.withValues(alpha: 0.05),
                    ],
                  ),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(20),
                  child: Column(
                    children: [
                      // Order ID
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Order ID:',
                            style: GoogleFonts.poppins(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: AppTheme.textColor,
                            ),
                          ),
                          Text(
                            orderId,
                            style: GoogleFonts.poppins(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: AppTheme.primaryColor,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),

                      // Current Status
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Current Status:',
                            style: GoogleFonts.poppins(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: AppTheme.textColor,
                            ),
                          ),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                            decoration: BoxDecoration(
                              color: AppTheme.accentColor.withValues(alpha: 0.2),
                              borderRadius: BorderRadius.circular(20),
                              border: Border.all(color: AppTheme.accentColor),
                            ),
                            child: Text(
                              currentStatus,
                              style: GoogleFonts.poppins(
                                fontSize: 14,
                                fontWeight: FontWeight.w600,
                                color: AppTheme.accentColor,
                              ),
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),

                      // Estimated Time
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Estimated Time:',
                            style: GoogleFonts.poppins(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: AppTheme.textColor,
                            ),
                          ),
                          Text(
                            estimatedTime,
                            style: GoogleFonts.poppins(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                              color: AppTheme.primaryColor,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
            const SizedBox(height: 32),

            // Progress Stages
            Text(
              'Order Progress',
              style: GoogleFonts.poppins(
                fontSize: 20,
                fontWeight: FontWeight.bold,
                color: AppTheme.textColor,
              ),
            ),
            const SizedBox(height: 24),

            // Progress Bar
            Column(
              children: List.generate(stages.length, (index) {
                final stage = stages[index];
                final isCompleted = stage['completed'] ?? false;
                final isCurrent = stage['current'] ?? false;
                
                return Column(
                  children: [
                    Row(
                      children: [
                        // Stage Icon
                        Container(
                          width: 50,
                          height: 50,
                          decoration: BoxDecoration(
                            shape: BoxShape.circle,
                            color: isCompleted 
                                ? AppTheme.accentColor 
                                : isCurrent 
                                    ? AppTheme.primaryColor 
                                    : AppTheme.textColor.withValues(alpha: 0.3),
                          ),
                          child: Icon(
                            stage['icon'],
                            color: Colors.white,
                            size: 24,
                          ),
                        ),
                        const SizedBox(width: 16),

                        // Stage Info
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                stage['name'],
                                style: GoogleFonts.poppins(
                                  fontSize: 16,
                                  fontWeight: FontWeight.w600,
                                  color: isCompleted || isCurrent 
                                      ? AppTheme.textColor 
                                      : AppTheme.textColor.withValues(alpha: 0.6),
                                ),
                              ),
                              if (isCurrent)
                                Text(
                                  'In progress...',
                                  style: GoogleFonts.poppins(
                                    fontSize: 12,
                                    color: AppTheme.accentColor,
                                  ),
                                ),
                            ],
                          ),
                        ),

                        // Status Icon
                        Icon(
                          isCompleted 
                              ? Icons.check_circle 
                              : isCurrent 
                                  ? Icons.pending 
                                  : Icons.radio_button_unchecked,
                          color: isCompleted 
                              ? AppTheme.accentColor 
                              : isCurrent 
                                  ? AppTheme.primaryColor 
                                  : AppTheme.textColor.withValues(alpha: 0.3),
                          size: 24,
                        ),
                      ],
                    ),

                    // Progress Line
                    if (index < stages.length - 1)
                      Container(
                        margin: const EdgeInsets.only(left: 25, top: 8, bottom: 8),
                        width: 2,
                        height: 30,
                        decoration: BoxDecoration(
                          color: isCompleted 
                              ? AppTheme.accentColor 
                              : AppTheme.textColor.withValues(alpha: 0.3),
                        ),
                      ),
                  ],
                );
              }),
            ),
            const SizedBox(height: 32),

            // Status Message
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppTheme.accentColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.accentColor.withValues(alpha: 0.3)),
              ),
              child: Column(
                children: [
                  Icon(
                    Icons.info_outline,
                    color: AppTheme.accentColor,
                    size: 32,
                  ),
                  const SizedBox(height: 12),
                  Text(
                    'Your order is being prepared with care!',
                    style: GoogleFonts.poppins(
                      fontSize: 16,
                      fontWeight: FontWeight.w600,
                      color: AppTheme.textColor,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'We\'ll notify you when it\'s ready for pickup.',
                    style: GoogleFonts.poppins(
                      fontSize: 14,
                      color: AppTheme.textColor.withValues(alpha: 0.7),
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
} 