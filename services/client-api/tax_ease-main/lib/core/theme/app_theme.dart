import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../constants/app_colors.dart';
import '../constants/app_dimensions.dart';
import 'app_typography.dart';

/// Premium app theme configuration for Tax Ease
class AppTheme {
  AppTheme._();

  /// Light theme configuration
  static ThemeData get lightTheme => ThemeData(
        useMaterial3: true,
        brightness: Brightness.light,
        
        // Diamond Accounts Color Scheme - Light Theme
        colorScheme: AppColors.lightColorScheme,

        // Typography
        textTheme: AppTypography.buildTextTheme(Brightness.light),
        
        // App bar theme
        appBarTheme: AppBarTheme(
          elevation: 0,
          centerTitle: true,
          backgroundColor: AppColors.backgroundLight,
          foregroundColor: AppColors.onBackgroundLight,
          titleTextStyle: AppTypography.buildTextTheme(Brightness.light).headlineSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: AppColors.onBackgroundLight,
          ),
          systemOverlayStyle: const SystemUiOverlayStyle(
            statusBarColor: Colors.transparent,
            statusBarIconBrightness: Brightness.dark,
            statusBarBrightness: Brightness.light,
          ),
        ),

        // Card theme
        cardTheme: CardThemeData(
          elevation: AppDimensions.cardElevation,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
          ),
          color: AppColors.surfaceLight,
          shadowColor: AppColors.shadowLight,
        ),

        // Elevated button theme
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            elevation: 2,
            backgroundColor: AppColors.brandPrimaryBlue,
            foregroundColor: AppColors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            ),
            padding: const EdgeInsets.symmetric(
              horizontal: AppDimensions.spacingLg,
              vertical: AppDimensions.spacingMd,
            ),
            minimumSize: const Size(0, AppDimensions.buttonHeightLg),
            textStyle: AppTypography.button,
          ),
        ),

        // Text button theme
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            foregroundColor: AppColors.brandPrimaryBlue,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            ),
            padding: const EdgeInsets.symmetric(
              horizontal: AppDimensions.spacingLg,
              vertical: AppDimensions.spacingMd,
            ),
          ),
        ),

        // Input decoration theme
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: AppColors.containerLight,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            borderSide: BorderSide(color: AppColors.grey300, width: 1),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            borderSide: BorderSide(color: AppColors.brandPrimaryBlue, width: 2),
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            borderSide: BorderSide(color: AppColors.error, width: 1),
          ),
          contentPadding: const EdgeInsets.all(AppDimensions.spacingMd),
          labelStyle: TextStyle(color: AppColors.grey600),
          hintStyle: TextStyle(color: AppColors.grey500),
        ),

        // Bottom navigation bar theme (using custom floating nav)
        // bottomNavigationBarTheme removed as we use custom implementation

        // Floating action button theme
        floatingActionButtonTheme: const FloatingActionButtonThemeData(
          backgroundColor: AppColors.brandPrimaryBlue,
          foregroundColor: AppColors.white,
          elevation: 4,
          shape: CircleBorder(),
        ),

        // Divider theme
        dividerTheme: const DividerThemeData(
          color: AppColors.grey200,
          thickness: 1,
          space: 1,
        ),

        // Page transitions for smooth animations
        pageTransitionsTheme: const PageTransitionsTheme(
          builders: {
            TargetPlatform.android: CupertinoPageTransitionsBuilder(),
            TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
            TargetPlatform.linux: FadeUpwardsPageTransitionsBuilder(),
            TargetPlatform.macOS: CupertinoPageTransitionsBuilder(),
            TargetPlatform.windows: FadeUpwardsPageTransitionsBuilder(),
          },
        ),

        // Scroll behavior for smooth scrolling
        scrollbarTheme: ScrollbarThemeData(
          thumbColor: WidgetStateProperty.all(AppColors.grey400),
          trackColor: WidgetStateProperty.all(AppColors.grey200),
          thickness: WidgetStateProperty.all(4.0),
          radius: const Radius.circular(AppDimensions.radiusSm),
        ),

        // Visual density for premium feel
        visualDensity: VisualDensity.adaptivePlatformDensity,
        
        // Splash factory for ripple effects
        splashFactory: InkRipple.splashFactory,
      );

  /// Dark theme configuration
  static ThemeData get darkTheme => ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        
        // Diamond Accounts Color Scheme - Dark Theme
        colorScheme: AppColors.darkColorScheme,

        // Typography
        textTheme: AppTypography.buildTextTheme(Brightness.dark),
        
        // App bar theme
        appBarTheme: AppBarTheme(
          elevation: 0,
          centerTitle: true,
          backgroundColor: AppColors.backgroundDark,
          foregroundColor: AppColors.onBackgroundDark,
          titleTextStyle: AppTypography.buildTextTheme(Brightness.dark).headlineSmall?.copyWith(
            fontWeight: FontWeight.w600,
            color: AppColors.onBackgroundDark,
          ),
          systemOverlayStyle: const SystemUiOverlayStyle(
            statusBarColor: Colors.transparent,
            statusBarIconBrightness: Brightness.light,
            statusBarBrightness: Brightness.dark,
          ),
        ),

        // Card theme
        cardTheme: CardThemeData(
          elevation: AppDimensions.cardElevation,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
          ),
          color: AppColors.surfaceDark,
          shadowColor: AppColors.shadowDark,
        ),

        // Elevated button theme for dark mode
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            elevation: 2,
            backgroundColor: AppColors.brandPrimaryBlue,
            foregroundColor: AppColors.white,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            ),
            padding: const EdgeInsets.symmetric(
              horizontal: AppDimensions.spacingLg,
              vertical: AppDimensions.spacingMd,
            ),
            minimumSize: const Size(0, AppDimensions.buttonHeightLg),
            textStyle: AppTypography.button,
          ),
        ),

        // Text button theme for dark mode
        textButtonTheme: TextButtonThemeData(
          style: TextButton.styleFrom(
            foregroundColor: AppColors.brandPrimaryBlue,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            ),
            padding: const EdgeInsets.symmetric(
              horizontal: AppDimensions.spacingLg,
              vertical: AppDimensions.spacingMd,
            ),
          ),
        ),

        // Input decoration theme for dark mode
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: AppColors.containerDark,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            borderSide: BorderSide.none,
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            borderSide: BorderSide(color: AppColors.grey600, width: 1),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            borderSide: BorderSide(color: AppColors.brandPrimaryBlue, width: 2),
          ),
          errorBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            borderSide: BorderSide(color: AppColors.error, width: 1),
          ),
          contentPadding: const EdgeInsets.all(AppDimensions.spacingMd),
          labelStyle: TextStyle(color: AppColors.grey400),
          hintStyle: TextStyle(color: AppColors.grey500),
        ),

        // Bottom navigation bar theme for dark mode (using custom floating nav)
        // bottomNavigationBarTheme removed as we use custom implementation

        // Floating action button theme for dark mode
        floatingActionButtonTheme: const FloatingActionButtonThemeData(
          backgroundColor: AppColors.brandPrimaryBlue,
          foregroundColor: AppColors.white,
          elevation: 4,
          shape: CircleBorder(),
        ),

        // Divider theme for dark mode
        dividerTheme: const DividerThemeData(
          color: AppColors.grey600,
          thickness: 1,
          space: 1,
        ),

        // Page transitions for smooth animations
        pageTransitionsTheme: const PageTransitionsTheme(
          builders: {
            TargetPlatform.android: CupertinoPageTransitionsBuilder(),
            TargetPlatform.iOS: CupertinoPageTransitionsBuilder(),
            TargetPlatform.linux: FadeUpwardsPageTransitionsBuilder(),
            TargetPlatform.macOS: CupertinoPageTransitionsBuilder(),
            TargetPlatform.windows: FadeUpwardsPageTransitionsBuilder(),
          },
        ),

        // Scroll behavior for smooth scrolling
        scrollbarTheme: ScrollbarThemeData(
          thumbColor: WidgetStateProperty.all(AppColors.grey400),
          trackColor: WidgetStateProperty.all(AppColors.grey700),
          thickness: WidgetStateProperty.all(4.0),
          radius: const Radius.circular(AppDimensions.radiusSm),
        ),

        // Visual density for premium feel
        visualDensity: VisualDensity.adaptivePlatformDensity,
        
        // Splash factory for ripple effects
        splashFactory: InkRipple.splashFactory,
      );

}
