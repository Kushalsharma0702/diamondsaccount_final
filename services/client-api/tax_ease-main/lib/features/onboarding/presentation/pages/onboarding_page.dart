import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:smooth_page_indicator/smooth_page_indicator.dart';
import 'package:flutter_svg/flutter_svg.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../shared/animations/smooth_animations.dart';

class OnboardingPage extends StatefulWidget {
  const OnboardingPage({super.key});

  @override
  State<OnboardingPage> createState() => _OnboardingPageState();
}

class _OnboardingPageState extends State<OnboardingPage> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<OnboardingItem> _items = [
    OnboardingItem(
      svgAsset: 'assets/on-boarding/page1.svg',
      title: 'Simplify Your Tax Filing',
      description:
          'No more confusing forms — file your taxes in minutes with expert guidance.',
    ),
    OnboardingItem(
      svgAsset: 'assets/on-boarding/page2.svg',
      title: 'Your Privacy, Our Priority',
      description:
          'We handle your financial information with top-grade encryption and data security standards.',
    ),
    OnboardingItem(
      svgAsset: 'assets/on-boarding/page3.svg',
      title: 'One-to-One Dedicated Support',
      description:
          'Get personalized assistance from our expert team — your dedicated advisor is just a message away.',
    ),
    OnboardingItem(
      svgAsset: 'assets/on-boarding/page4.svg',
      title: 'Maximize Your Savings',
      description:
          'Our intelligent system identifies every eligible deduction and credit to help you keep more of what you earn.',
    ),
  ];

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            // Skip button
            Align(
              alignment: Alignment.centerRight,
              child: Padding(
                padding: const EdgeInsets.all(AppDimensions.spacingMd),
                child: TextButton(
                  onPressed: () => _navigateToAuth(),
                  child: Text(
                    'Skip',
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: AppColors.grey600,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ),
              ),
            ),

            // Page view content
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                onPageChanged: (index) {
                  setState(() {
                    _currentPage = index;
                  });
                },
                itemCount: _items.length,
                itemBuilder: (context, index) {
                  return Padding(
                    padding: const EdgeInsets.all(AppDimensions.screenPadding),
                    child: SmoothAnimations.fadeIn(
                      duration: const Duration(milliseconds: 600),
                      child: _buildOnboardingItem(_items[index]),
                    ),
                  );
                },
              ),
            ),

            // Bottom section with indicator and buttons
            Padding(
              padding: const EdgeInsets.all(AppDimensions.screenPadding),
              child: Column(
                children: [
                  // Page indicator
                  SmoothPageIndicator(
                    controller: _pageController,
                    count: _items.length,
                    effect: WormEffect(
                      dotColor: AppColors.grey300,
                      activeDotColor: AppColors.primary,
                      dotHeight: 8,
                      dotWidth: 8,
                      spacing: 16,
                    ),
                  ),

                  const SizedBox(height: 40),

                  // Buttons
                  Row(
                    children: [
                      if (_currentPage > 0)
                        Expanded(
                          child: TextButton(
                            onPressed: () {
                              _pageController.previousPage(
                                duration: const Duration(milliseconds: 300),
                                curve: Curves.easeInOut,
                              );
                            },
                            style: TextButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 16),
                            ),
                            child: Text(
                              'Previous',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                color: AppColors.grey600,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),
                        ),
                      
                      if (_currentPage > 0) const SizedBox(width: 16),

                      Expanded(
                        flex: _currentPage == 0 ? 1 : 2,
                        child: ElevatedButton(
                          onPressed: _currentPage == _items.length - 1
                              ? _navigateToAuth
                              : () {
                                  _pageController.nextPage(
                                    duration: const Duration(milliseconds: 300),
                                    curve: Curves.easeInOut,
                                  );
                                },
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                          ),
                          child: Text(
                            _currentPage == _items.length - 1 ? 'Get Started' : 'Next',
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.w600,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 16),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOnboardingItem(OnboardingItem item) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        // SVG Illustration
        SizedBox(
          width: 280,
          height: 280,
          child: SvgPicture.asset(
            item.svgAsset,
            fit: BoxFit.contain,
          ),
        ),

        const SizedBox(height: 40),

        // Title
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            item.title,
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              color: AppColors.grey800,
              fontWeight: FontWeight.bold,
            ),
            textAlign: TextAlign.center,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
          ),
        ),

        const SizedBox(height: 16),

        // Description
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16),
          child: Text(
            item.description,
            style: Theme.of(context).textTheme.bodyLarge?.copyWith(
              color: AppColors.grey600,
              height: 1.5,
            ),
            textAlign: TextAlign.center,
            maxLines: 4,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }

  void _navigateToAuth() {
    context.go('/signup');
  }
}

class OnboardingItem {
  final String svgAsset;
  final String title;
  final String description;

  OnboardingItem({
    required this.svgAsset,
    required this.title,
    required this.description,
  });
}
