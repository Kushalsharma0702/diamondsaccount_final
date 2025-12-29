import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_colors.dart';

class MainScaffold extends StatelessWidget {
  final Widget child;
  final String currentPath;

  const MainScaffold({
    super.key,
    required this.child,
    required this.currentPath,
  });

  @override
  Widget build(BuildContext context) {
    return PopScope(
      canPop: currentPath == '/home',
      onPopInvokedWithResult: (didPop, result) {
        if (didPop) return;
        
        // Handle back button navigation
        if (currentPath == '/home') {
          // Exit app when on home page
          SystemNavigator.pop();
        } else {
          // Navigate to home for other bottom nav screens
          context.go('/home');
        }
      },
      child: Scaffold(
        body: Stack(
          children: [
            // Main content that goes behind the floating nav
            child,
            // Floating bottom navigation
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: _BottomNavigationBar(currentPath: currentPath),
            ),
          ],
        ),
      ),
    );
  }
}

class _BottomNavigationBar extends StatefulWidget {
  final String currentPath;
  const _BottomNavigationBar({required this.currentPath});

  @override
  State<_BottomNavigationBar> createState() => _BottomNavigationBarState();
}

class _BottomNavigationBarState extends State<_BottomNavigationBar> {
  @override
  Widget build(BuildContext context) {
    // Always read the router's current location so the highlight updates on navigation
    final String location = widget.currentPath;

    debugPrint('Current location: $location');

    return Container(
      height: 68, // Compact height to prevent overflow
      margin: const EdgeInsets.all(16),
      child: Stack(
        children: [
          // Background blur effect for floating appearance
          Positioned.fill(
            child: Container(
              decoration: BoxDecoration(
                color: AppColors.primary, // Fill pill with highlight color
                borderRadius: BorderRadius.circular(35),
                boxShadow: [
                  BoxShadow(
                    color: AppColors.primary.withValues(alpha: 0.35),
                    blurRadius: 24,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
            ),
          ),
          // Navigation items
          // Center icons vertically within the pill
          Center(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 12.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  _buildNavItem(
                    context: context,
                    icon: Icons.home_outlined,
                    activeIcon: Icons.home,
                    route: '/home',
                    isActive: location == '/home',
                  ),
                  _buildNavItem(
                    context: context,
                    icon: Icons.description_outlined,
                    activeIcon: Icons.description,
                    route: '/tax-forms/filled-forms',
                    isActive: location.startsWith('/tax-forms'),
                  ),
                  _buildNavItem(
                    context: context,
                    icon: Icons.folder_outlined,
                    activeIcon: Icons.folder,
                    route: '/documents',
                    isActive: location.startsWith('/documents'),
                  ),
                  _buildNavItem(
                    context: context,
                    icon: Icons.person_outline,
                    activeIcon: Icons.person,
                    route: '/profile',
                    isActive: location == '/profile',
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNavItem({
    required BuildContext context,
    required IconData icon,
    required IconData activeIcon,
    required String route,
    required bool isActive,
  }) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    
    return Expanded(
      child: GestureDetector(
        onTap: () {
          debugPrint('Tapping route: $route');
          context.go(route);
        },
        behavior: HitTestBehavior.opaque,
        child: Center(
          child: AnimatedContainer(
            duration: const Duration(milliseconds: 250),
            curve: Curves.easeOutCubic,
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              color: isActive ? AppColors.white.withValues(alpha: 0.15) : Colors.transparent,
              shape: BoxShape.circle,
            ),
            child: AnimatedSwitcher(
              duration: const Duration(milliseconds: 200),
              child: Icon(
                isActive ? activeIcon : icon,
                key: ValueKey('${route}_$isActive'),
                color: isActive
                    ? AppColors.white
                    : (isDark ? AppColors.grey400 : AppColors.grey600),
                size: 22,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
