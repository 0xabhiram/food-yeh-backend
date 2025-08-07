import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:go_router/go_router.dart';
import 'core/theme/app_theme.dart';
import 'core/constants/app_constants.dart';
import 'services/auth_service.dart';
import 'services/api_service.dart';
import 'screens/login_screen.dart';
import 'screens/dashboard_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize services
  ApiService().initialize();
  final authService = AuthService();
  await authService.initialize();
  
  runApp(MyApp(authService: authService));
}

class MyApp extends StatelessWidget {
  final AuthService authService;

  const MyApp({super.key, required this.authService});

  @override
  Widget build(BuildContext context) {
    return ChangeNotifierProvider.value(
      value: authService,
      child: MaterialApp.router(
        title: AppConstants.appName,
        debugShowCheckedModeBanner: false,
        theme: AppTheme.darkTheme,
        routerConfig: _createRouter(),
      ),
    );
  }

  GoRouter _createRouter() {
    return GoRouter(
      initialLocation: '/',
      redirect: (context, state) {
        final authService = Provider.of<AuthService>(context, listen: false);
        final isLoggedIn = authService.isLoggedIn;
        final isLoginRoute = state.matchedLocation == '/login';

        // If not logged in and not on login page, redirect to login
        if (!isLoggedIn && !isLoginRoute) {
          return '/login';
        }

        // If logged in and on login page, redirect to dashboard
        if (isLoggedIn && isLoginRoute) {
          return '/dashboard';
        }

        return null;
      },
      routes: [
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/dashboard',
          builder: (context, state) => const DashboardScreen(),
        ),
        // Add more routes as needed
        GoRoute(
          path: '/',
          redirect: (context, state) => '/dashboard',
        ),
      ],
      errorBuilder: (context, state) => _buildErrorScreen(state.error),
    );
  }

  Widget _buildErrorScreen(Exception? error) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Error'),
      ),
      body: Center(
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
              'Page not found',
              style: TextStyle(
                color: AppTheme.errorRed,
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              'The page you are looking for does not exist.',
              style: TextStyle(
                color: AppTheme.grey,
                fontSize: 14,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 16),
            CustomButton(
              onPressed: () => GoRouter.of(context).go('/dashboard'),
              child: const Text('Go to Dashboard'),
            ),
          ],
        ),
      ),
    );
  }
}

// Custom Button widget for error screen
class CustomButton extends StatelessWidget {
  final VoidCallback? onPressed;
  final Widget child;

  const CustomButton({
    super.key,
    this.onPressed,
    required this.child,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      child: child,
    );
  }
} 