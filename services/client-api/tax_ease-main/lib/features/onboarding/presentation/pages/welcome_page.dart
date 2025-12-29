import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../shared/animations/smooth_animations.dart';

class WelcomePage extends StatefulWidget {
  const WelcomePage({super.key});

  @override
  State<WelcomePage> createState() => _WelcomePageState();
}

class _WelcomePageState extends State<WelcomePage>
    with TickerProviderStateMixin {
  late AnimationController _fadeController;
  late AnimationController _scaleController;
  late AnimationController _slideController;
  late AnimationController _backgroundController;
  
  
  @override
  void initState() {
    super.initState();
    
    // Initialize animation controllers
    _fadeController = AnimationController(
      duration: const Duration(milliseconds: 1200),
      vsync: this,
    );
    _scaleController = AnimationController(
      duration: const Duration(milliseconds: 800),
      vsync: this,
    );
    _slideController = AnimationController(
      duration: const Duration(milliseconds: 1000),
      vsync: this,
    );
    _backgroundController = AnimationController(
      duration: const Duration(milliseconds: 1500),
      vsync: this,
    );
    
    
    // Start staggered animations
    _startAnimations();
  }
  
  void _startAnimations() {
    // Background animation starts immediately
    _backgroundController.forward();
    
    // Logo scale animation starts after a brief delay
    Future.delayed(const Duration(milliseconds: 200), () {
      if (mounted) _scaleController.forward();
    });
    
    // Fade in text elements
    Future.delayed(const Duration(milliseconds: 500), () {
      if (mounted) _fadeController.forward();
    });
    
    // Slide up additional elements
    Future.delayed(const Duration(milliseconds: 700), () {
      if (mounted) _slideController.forward();
    });
  }
  
  @override
  void dispose() {
    _fadeController.dispose();
    _scaleController.dispose();
    _slideController.dispose();
    _backgroundController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: AppColors.primaryGradient,
        ),
        child: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(AppDimensions.screenPadding),
            child: Column(
              children: [
                Expanded(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      // App Logo with smooth scale animation
                      ScaleTransition(
                        scale: CurvedAnimation(
                          parent: _scaleController,
                          curve: Curves.elasticOut,
                        ),
                        child: Container(
                          width: 120,
                          height: 120,
                          decoration: BoxDecoration(
                            color: AppColors.white,
                            borderRadius: BorderRadius.circular(30),
                            boxShadow: [
                              BoxShadow(
                                color: AppColors.shadowDark,
                                blurRadius: 20,
                                offset: const Offset(0, 10),
                              ),
                            ],
                          ),
                          child: const Icon(
                            Icons.receipt_long_rounded,
                            size: 60,
                            color: AppColors.primary,
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 40),
                      
                      // App Name with fade animation
                      FadeTransition(
                        opacity: _fadeController,
                        child: Text(
                          'TaxEase',
                          style: Theme.of(context).textTheme.headlineLarge?.copyWith(
                            color: AppColors.white,
                            fontWeight: FontWeight.bold,
                          ),
                          textAlign: TextAlign.center,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      // App Tagline
                      SmoothAnimations.slideUp(
                        delay: const Duration(milliseconds: 800),
                        child: Padding(
                          padding: const EdgeInsets.symmetric(horizontal: 16),
                          child: Text(
                            'Simplify your tax filing process\nwith secure and efficient solutions',
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              color: AppColors.white.withValues(alpha: 0.9),
                              fontWeight: FontWeight.w400,
                            ),
                            textAlign: TextAlign.center,
                            maxLines: 3,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 48),
                      
                      // Features list
                      SmoothAnimations.slideUp(
                        delay: const Duration(milliseconds: 1000),
                        child: Column(
                          children: [
                            _buildFeatureItem(
                              icon: Icons.security_rounded,
                              text: 'Secure document upload',
                            ),
                            const SizedBox(height: 12),
                            _buildFeatureItem(
                              icon: Icons.track_changes_rounded,
                              text: 'Real-time status tracking',
                            ),
                            const SizedBox(height: 12),
                            _buildFeatureItem(
                              icon: Icons.download_rounded,
                              text: 'Downloadable tax summaries',
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                
                // Bottom buttons
                SmoothAnimations.slideUp(
                  delay: const Duration(milliseconds: 1200),
                  child: Column(
                    children: [
                      // Get Started Button
                      SizedBox(
                        width: double.infinity,
                        height: 56,
                        child: ElevatedButton(
                          onPressed: () => context.go('/onboarding'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: AppColors.white,
                            foregroundColor: AppColors.primary,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(28),
                            ),
                          ),
                          child: Text(
                            'Get Started',
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              color: AppColors.primary,
                              fontWeight: FontWeight.w600,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 16),
                      
                      // Already have account button
                      SizedBox(
                        width: double.infinity,
                        height: 56,
                        child: TextButton(
                          onPressed: () => context.go('/login'),
                          style: TextButton.styleFrom(
                            foregroundColor: AppColors.white,
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(28),
                              side: const BorderSide(
                                color: AppColors.white,
                                width: 1.5,
                              ),
                            ),
                          ),
                          child: Text(
                            'I already have an account',
                            style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              color: AppColors.white,
                              fontWeight: FontWeight.w500,
                            ),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                        ),
                      ),
                      
                      const SizedBox(height: 24),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
  
  Widget _buildFeatureItem({
    required IconData icon,
    required String text,
  }) {
    return Row(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: AppColors.white.withValues(alpha: 0.2),
            borderRadius: BorderRadius.circular(20),
          ),
          child: Icon(
            icon,
            color: AppColors.white,
            size: 20,
          ),
        ),
        const SizedBox(width: 16),
        Expanded(
          child: Text(
            text,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: AppColors.white.withValues(alpha: 0.85),
              fontWeight: FontWeight.w400,
            ),
          ),
        ),
      ],
    );
  }
}
