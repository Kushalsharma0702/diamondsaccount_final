import 'package:flutter/material.dart';

/// Diamond Accounts color palette for Tax Ease app with professional blue theme
class AppColors {
  AppColors._();

  // ===== CORE BRAND COLORS =====
  /// Foundational colors derived directly from the Diamond Accounts logo
  static const Color brandPrimaryBlue = Color(0xFF1E50A0); // Primary Blue
  static const Color brandDarkerBlue = Color(0xFF0A2B68); // Darker Accent Blue
  static const Color brandLightBlue = Color(0xFF4A8CDA); // Light Accent Blue

  // ===== LIGHT THEME COLORS =====
  /// Light theme palette for bright environments - clean, professional, airy
  static const Color primaryLight = Color(0xFF1E50A0); // Primary Color
  static const Color onPrimaryLight = Color(0xFFFFFFFF); // On Primary Color
  static const Color secondaryLight = Color(0xFF4A8CDA); // Secondary Color
  static const Color onSecondaryLight = Color(0xFFFFFFFF); // On Secondary Color
  static const Color backgroundLight = Color(0xFFF5F7FA); // Background Color - soft grey
  static const Color onBackgroundLight = Color(0xFF212121); // On Background Color
  static const Color surfaceLight = Color(0xFFFFFFFF); // Surface Color
  static const Color onSurfaceLight = Color(0xFF212121); // On Surface Color
  static const Color errorLight = Color(0xFFD32F2F); // Error Color
  static const Color onErrorLight = Color(0xFFFFFFFF); // On Error Color

  // ===== DARK THEME COLORS =====
  /// Dark theme palette for low-light conditions - modern, premium feel
  static const Color primaryDark = Color(0xFF4A8CDA); // Primary Color (lighter blue for contrast)
  static const Color onPrimaryDark = Color(0xFFFFFFFF); // On Primary Color
  static const Color secondaryDark = Color(0xFF1E50A0); // Secondary Color (main brand blue)
  static const Color onSecondaryDark = Color(0xFFFFFFFF); // On Secondary Color
  static const Color backgroundDark = Color(0xFF0D1A2E); // Background Color - deep dark blue
  static const Color onBackgroundDark = Color(0xFFE0E0E0); // On Background Color - soft white
  static const Color surfaceDark = Color(0xFF1A2B47); // Surface Color - slightly lighter than background
  static const Color onSurfaceDark = Color(0xFFFFFFFF); // On Surface Color
  static const Color errorDark = Color(0xFFEF5350); // Error Color - brighter red for dark surfaces
  static const Color onErrorDark = Color(0xFF000000); // On Error Color

  // ===== LEGACY COMPATIBILITY COLORS =====
  /// For backward compatibility with existing code
  static const Color primary = brandPrimaryBlue;
  static const Color secondary = brandLightBlue;
  static const Color accent = brandLightBlue;
  static const Color accentLight = Color(0xFF87CEEB); // Sky blue
  static const Color accentDark = brandDarkerBlue;
  
  // ===== NEUTRAL COLORS =====
  static const Color white = Color(0xFFFFFFFF);
  static const Color black = Color(0xFF000000);
  static const Color grey50 = Color(0xFFFAFAFA);
  static const Color grey100 = Color(0xFFF5F5F5);
  static const Color grey200 = Color(0xFFEEEEEE);
  static const Color grey300 = Color(0xFFE0E0E0);
  static const Color grey400 = Color(0xFFBDBDBD);
  static const Color grey500 = Color(0xFF9E9E9E);
  static const Color grey600 = Color(0xFF757575);
  static const Color grey700 = Color(0xFF616161);
  static const Color grey800 = Color(0xFF424242);
  static const Color grey900 = Color(0xFF212121);
  
  // ===== STATUS COLORS =====
  /// Status colors that work well with the Diamond Accounts theme
  static const Color success = Color(0xFF4CAF50); // Green
  static const Color warning = Color(0xFFFF9800); // Orange
  static const Color error = Color(0xFFD32F2F); // Red (light theme error)
  static const Color info = Color(0xFF2196F3); // Blue
  
  // ===== SURFACE & CONTAINER COLORS =====
  /// Updated surface and container colors using Diamond Accounts palette
  
  // Legacy compatibility - use theme-specific colors instead
  static const Color surface = surfaceLight;
  static const Color cardLight = surfaceLight;
  static const Color cardDark = surfaceDark;
  static const Color containerLight = Color(0xFFF0F2F5); // Slightly darker than background
  static const Color containerDark = Color(0xFF243A5C); // Slightly lighter than surface
  
  // ===== DIAMOND ACCOUNTS GRADIENTS =====
  /// Premium gradient animations using Diamond Accounts blue palette
  
  /// Primary brand gradient (light to dark blue)
  static const LinearGradient brandGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [brandLightBlue, brandPrimaryBlue, brandDarkerBlue],
  );
  
  /// Light theme gradient
  static const LinearGradient lightGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [secondaryLight, primaryLight, brandDarkerBlue],
  );
  
  /// Dark theme gradient
  static const LinearGradient darkGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [primaryDark, secondaryDark, brandDarkerBlue],
  );
  
  /// Legacy compatibility gradients
  static const LinearGradient primaryGradient = brandGradient;
  static const LinearGradient secondaryGradient = lightGradient;
  static const LinearGradient accentGradient = brandGradient;
  
  // ===== SHADOW COLORS =====
  /// Shadow colors for depth and elevation
  static const Color shadowLight = Color(0x1A000000);
  static const Color shadowMedium = Color(0x33000000);
  static const Color shadowDark = Color(0x4D000000);
  
  // ===== FLUTTER COLORSCHEME DEFINITIONS =====
  /// Complete Flutter ColorScheme objects for seamless Material 3 integration
  
  /// Light theme ColorScheme - Diamond Accounts style
  static const ColorScheme lightColorScheme = ColorScheme(
    brightness: Brightness.light,
    primary: primaryLight,
    onPrimary: onPrimaryLight,
    secondary: secondaryLight,
    onSecondary: onSecondaryLight,
    error: errorLight,
    onError: onErrorLight,
    surface: surfaceLight,
    onSurface: onSurfaceLight,
    // Additional Material 3 colors
    primaryContainer: Color(0xFFD4E3FF), // Light blue container
    onPrimaryContainer: Color(0xFF001B3D), // Dark blue text
    secondaryContainer: Color(0xFFE3F2FD), // Very light blue container
    onSecondaryContainer: Color(0xFF0D1F2D), // Dark text
    tertiary: Color(0xFF5A6B7C), // Blue-grey
    onTertiary: white,
    tertiaryContainer: Color(0xFFE1F5FE), // Light blue-grey container
    onTertiaryContainer: Color(0xFF0F1419), // Dark text
    errorContainer: Color(0xFFFFDAD6), // Light red container
    onErrorContainer: Color(0xFF410002), // Dark red text
    outline: Color(0xFF73777F), // Blue-grey outline
    outlineVariant: Color(0xFFC3C7CF), // Light outline
    surfaceContainerHighest: Color(0xFFE1E2EC), // Light blue-grey surface
    onSurfaceVariant: Color(0xFF44474E), // Dark text
    inverseSurface: Color(0xFF2E3132), // Dark surface for contrast
    onInverseSurface: Color(0xFFF0F0F3), // Light text on dark
    inversePrimary: primaryDark, // Light primary on dark
    shadow: shadowLight,
    scrim: black,
    surfaceTint: primaryLight,
  );
  
  /// Dark theme ColorScheme - Diamond Accounts style
  static const ColorScheme darkColorScheme = ColorScheme(
    brightness: Brightness.dark,
    primary: primaryDark,
    onPrimary: onPrimaryDark,
    secondary: secondaryDark,
    onSecondary: onSecondaryDark,
    error: errorDark,
    onError: onErrorDark,
    surface: surfaceDark,
    onSurface: onSurfaceDark,
    // Additional Material 3 colors for dark theme
    primaryContainer: Color(0xFF003A75), // Dark blue container
    onPrimaryContainer: Color(0xFFD4E3FF), // Light blue text
    secondaryContainer: Color(0xFF0F2943), // Very dark blue container
    onSecondaryContainer: Color(0xFFB8E6FF), // Light blue text
    tertiary: Color(0xFF9BB0C4), // Light blue-grey
    onTertiary: Color(0xFF253340), // Dark background
    tertiaryContainer: Color(0xFF3B4957), // Dark blue-grey container
    onTertiaryContainer: Color(0xFFB7CCE0), // Light text
    errorContainer: Color(0xFF93000A), // Dark red container
    onErrorContainer: Color(0xFFFFDAD6), // Light red text
    outline: Color(0xFF8D9199), // Light outline for dark
    outlineVariant: Color(0xFF44474E), // Dark outline
    surfaceContainerHighest: Color(0xFF44474E), // Dark blue-grey surface
    onSurfaceVariant: Color(0xFFC3C7CF), // Light text
    inverseSurface: Color(0xFFE1E2E8), // Light surface for contrast
    onInverseSurface: Color(0xFF2E3132), // Dark text on light
    inversePrimary: primaryLight, // Dark primary on light
    shadow: shadowDark,
    scrim: black,
    surfaceTint: primaryDark,
  );
}
