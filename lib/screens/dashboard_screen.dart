import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'dart:async';
import '../core/theme/app_theme.dart';
import '../core/constants/app_constants.dart';
import '../services/auth_service.dart';
import '../services/api_service.dart';
import '../models/order.dart';
import '../models/system_status.dart';
import '../widgets/custom_button.dart';
import '../widgets/status_card.dart';
import '../widgets/order_card.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  Timer? _refreshTimer;
  bool _isLoading = true;
  String? _errorMessage;

  // Dashboard data
  List<Order> _recentOrders = [];
  HealthCheck? _healthStatus;
  MqttStatus? _mqttStatus;
  SystemInfo? _systemInfo;
  int _totalOrders = 0;
  int _pendingOrders = 0;
  int _completedOrders = 0;
  double _totalRevenue = 0.0;

  @override
  void initState() {
    super.initState();
    _loadDashboardData();
    _startRefreshTimer();
  }

  @override
  void dispose() {
    _refreshTimer?.cancel();
    super.dispose();
  }

  void _startRefreshTimer() {
    _refreshTimer = Timer.periodic(
      AppConstants.dashboardRefreshInterval,
      (_) => _loadDashboardData(),
    );
  }

  Future<void> _loadDashboardData() async {
    if (!mounted) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      await Future.wait([
        _loadHealthStatus(),
        _loadMqttStatus(),
        _loadSystemInfo(),
        _loadRecentOrders(),
        _loadOrderStats(),
      ]);
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMessage = e.toString();
        });
      }
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _loadHealthStatus() async {
    try {
      final health = await ApiService().getHealthStatus();
      if (mounted) {
        setState(() {
          _healthStatus = health;
        });
      }
    } catch (e) {
      // Handle error silently for health check
    }
  }

  Future<void> _loadMqttStatus() async {
    try {
      final mqtt = await ApiService().getMqttStatus();
      if (mounted) {
        setState(() {
          _mqttStatus = mqtt;
        });
      }
    } catch (e) {
      // Handle error silently for MQTT status
    }
  }

  Future<void> _loadSystemInfo() async {
    try {
      final system = await ApiService().getSystemInfo();
      if (mounted) {
        setState(() {
          _systemInfo = system;
        });
      }
    } catch (e) {
      // Handle error silently for system info
    }
  }

  Future<void> _loadRecentOrders() async {
    try {
      final response = await ApiService().getOrders(page: 1, perPage: 5);
      if (mounted) {
        setState(() {
          _recentOrders = response.orders;
        });
      }
    } catch (e) {
      // Handle error silently for recent orders
    }
  }

  Future<void> _loadOrderStats() async {
    try {
      final response = await ApiService().getOrders(page: 1, perPage: 100);
      if (mounted) {
        setState(() {
          _totalOrders = response.total;
          _pendingOrders = response.orders.where((o) => o.isPending).length;
          _completedOrders = response.orders.where((o) => o.isCompleted).length;
          _totalRevenue = response.orders.fold(0.0, (sum, order) => sum + order.totalAmount);
        });
      }
    } catch (e) {
      // Handle error silently for order stats
    }
  }

  @override
  Widget build(BuildContext context) {
    final authService = Provider.of<AuthService>(context);
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('Dashboard'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadDashboardData,
            tooltip: 'Refresh',
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              switch (value) {
                case 'profile':
                  Navigator.pushNamed(context, '/profile');
                  break;
                case 'logout':
                  _showLogoutDialog();
                  break;
              }
            },
            itemBuilder: (context) => [
              PopupMenuItem(
                value: 'profile',
                child: Row(
                  children: const [
                    Icon(Icons.person, color: AppTheme.primaryYellow),
                    SizedBox(width: 8),
                    Text('Profile'),
                  ],
                ),
              ),
              const PopupMenuDivider(),
              PopupMenuItem(
                value: 'logout',
                child: Row(
                  children: const [
                    Icon(Icons.logout, color: AppTheme.errorRed),
                    SizedBox(width: 8),
                    Text('Logout'),
                  ],
                ),
              ),
            ],
            child: CircleAvatar(
              backgroundColor: AppTheme.primaryYellow,
              child: Text(
                authService.userDisplayName.substring(0, 1).toUpperCase(),
                style: const TextStyle(
                  color: AppTheme.primaryBlack,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _errorMessage != null
              ? _buildErrorWidget()
              : RefreshIndicator(
                  onRefresh: _loadDashboardData,
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Welcome Section
                        _buildWelcomeSection(authService),
                        const SizedBox(height: 24),
                        
                        // Status Cards
                        _buildStatusCards(),
                        const SizedBox(height: 24),
                        
                        // System Health
                        _buildSystemHealthSection(),
                        const SizedBox(height: 24),
                        
                        // Recent Orders
                        _buildRecentOrdersSection(),
                      ],
                    ),
                  ),
                ),
      floatingActionButton: CustomFloatingActionButton(
        onPressed: () => Navigator.pushNamed(context, '/orders'),
        child: const Icon(Icons.list_alt),
        tooltip: 'View All Orders',
      ),
    );
  }

  Widget _buildWelcomeSection(AuthService authService) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: AppTheme.cardGradient,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryYellow.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.waving_hand,
                color: AppTheme.primaryYellow,
                size: 24,
              ),
              const SizedBox(width: 8),
              Text(
                'Welcome back, ${authService.userDisplayName}!',
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                  color: AppTheme.white,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            'Here\'s what\'s happening with your vending machine today.',
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: AppTheme.grey,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusCards() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 16,
      mainAxisSpacing: 16,
      childAspectRatio: 1.5,
      children: [
        StatusCard(
          title: 'Total Orders',
          value: _totalOrders.toString(),
          icon: Icons.shopping_cart,
          color: AppTheme.primaryYellow,
          subtitle: 'All time',
        ),
        StatusCard(
          title: 'Pending Orders',
          value: _pendingOrders.toString(),
          icon: Icons.pending,
          color: AppTheme.warningOrange,
          subtitle: 'Awaiting processing',
        ),
        StatusCard(
          title: 'Completed Orders',
          value: _completedOrders.toString(),
          icon: Icons.check_circle,
          color: AppTheme.successGreen,
          subtitle: 'Successfully processed',
        ),
        StatusCard(
          title: 'Total Revenue',
          value: '\$${_totalRevenue.toStringAsFixed(2)}',
          icon: Icons.attach_money,
          color: AppTheme.infoBlue,
          subtitle: 'All time earnings',
        ),
      ],
    );
  }

  Widget _buildSystemHealthSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'System Health',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            color: AppTheme.white,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        Row(
          children: [
            Expanded(
              child: _buildHealthCard(
                'Overall Status',
                _healthStatus?.statusDisplay ?? 'Unknown',
                _healthStatus?.isHealthy == true ? AppTheme.successGreen : AppTheme.errorRed,
                Icons.health_and_safety,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: _buildHealthCard(
                'MQTT Status',
                _mqttStatus?.statusDisplay ?? 'Unknown',
                _mqttStatus?.connected == true ? AppTheme.successGreen : AppTheme.errorRed,
                Icons.wifi,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildHealthCard(String title, String status, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.secondaryBlack,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 20),
              const SizedBox(width: 8),
              Text(
                title,
                style: TextStyle(
                  color: AppTheme.white,
                  fontWeight: FontWeight.w600,
                  fontSize: 14,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            status,
            style: TextStyle(
              color: color,
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecentOrdersSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'Recent Orders',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                color: AppTheme.white,
                fontWeight: FontWeight.bold,
              ),
            ),
            TextButton(
              onPressed: () => Navigator.pushNamed(context, '/orders'),
              child: const Text('View All'),
            ),
          ],
        ),
        const SizedBox(height: 16),
        if (_recentOrders.isEmpty)
          Container(
            padding: const EdgeInsets.all(32),
            child: Column(
              children: [
                Icon(
                  Icons.shopping_cart_outlined,
                  size: 48,
                  color: AppTheme.grey,
                ),
                const SizedBox(height: 16),
                Text(
                  'No orders yet',
                  style: TextStyle(
                    color: AppTheme.grey,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          )
        else
          ListView.builder(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _recentOrders.length,
            itemBuilder: (context, index) {
              return OrderCard(
                order: _recentOrders[index],
                onTap: () => Navigator.pushNamed(
                  context,
                  '/order-details',
                  arguments: _recentOrders[index].orderId,
                ),
              );
            },
          ),
      ],
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.error_outline,
            size: 64,
            color: AppTheme.errorRed,
          ),
          const SizedBox(height: 16),
          Text(
            'Failed to load dashboard',
            style: TextStyle(
              color: AppTheme.errorRed,
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            _errorMessage ?? 'Unknown error occurred',
            style: TextStyle(
              color: AppTheme.grey,
              fontSize: 14,
            ),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          CustomButton(
            onPressed: _loadDashboardData,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  void _showLogoutDialog() {
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
              Provider.of<AuthService>(context, listen: false).logout();
              Navigator.pushReplacementNamed(context, '/login');
            },
            child: const Text('Logout'),
          ),
        ],
      ),
    );
  }
} 