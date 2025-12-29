/// Premium spacing and dimension constants for Tax Ease app
class AppDimensions {
  AppDimensions._();

  // Base spacing unit
  static const double baseUnit = 8.0;

  // Spacing constants
  static const double spacing2xs = baseUnit * 0.25; // 2.0
  static const double spacingXs = baseUnit * 0.5;   // 4.0
  static const double spacingSm = baseUnit;          // 8.0
  static const double spacingMd = baseUnit * 2;     // 16.0
  static const double spacingLg = baseUnit * 3;     // 24.0
  static const double spacingXl = baseUnit * 4;     // 32.0
  static const double spacing2xl = baseUnit * 6;    // 48.0
  static const double spacing3xl = baseUnit * 8;    // 64.0

  // Border radius for premium look
  static const double radiusXs = 2.0;
  static const double radiusSm = 4.0;
  static const double radiusMd = 8.0;
  static const double radiusLg = 12.0;
  static const double radiusXl = 16.0;
  static const double radius2xl = 24.0;
  static const double radius3xl = 32.0;

  // Icon sizes
  static const double iconXs = 12.0;
  static const double iconSm = 16.0;
  static const double iconMd = 20.0;
  static const double iconLg = 24.0;
  static const double iconXl = 32.0;
  static const double icon2xl = 48.0;
  static const double icon3xl = 64.0;

  // Button dimensions
  static const double buttonHeightSm = 32.0;
  static const double buttonHeightMd = 40.0;
  static const double buttonHeightLg = 48.0;
  static const double buttonHeightXl = 56.0;

  // Minimum touch target size for accessibility
  static const double minTouchTarget = 44.0;

  // App bar height
  static const double appBarHeight = 56.0;
  static const double toolbarHeight = 56.0;

  // Bottom navigation
  static const double bottomNavHeight = 80.0;
  static const double bottomNavIconSize = 24.0;

  // Card and container dimensions
  static const double cardElevation = 4.0;
  static const double cardElevationHigh = 8.0;
  static const double containerMinHeight = 48.0;

  // Screen padding
  static const double screenPadding = spacingMd;
  static const double screenPaddingLarge = spacingLg;

  // Maximum content width for larger screens
  static const double maxContentWidth = 600.0;
  static const double maxDialogWidth = 400.0;

  // Animation durations (in milliseconds)
  static const int animationDurationFast = 200;
  static const int animationDurationMedium = 300;
  static const int animationDurationSlow = 500;
  static const int animationDurationVerySlow = 1000;

  // Scroll physics constants
  static const double scrollPhysicsSpring = 0.5;
  static const double scrollPhysicsDamping = 0.9;
}
