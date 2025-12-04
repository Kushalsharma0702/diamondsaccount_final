import 'package:flutter/material.dart';

/// Responsive utility class that provides helper methods and widgets
/// to enable responsive layouts, font scaling, spacing, and container width limits
/// for mobile, tablet, and desktop
class Responsive {
  static const double mobileBreakpoint = 600;
  static const double tabletBreakpoint = 1024;
  
  // Maximum container widths for different screen sizes
  static const double maxMobileWidth = 480;
  static const double maxTabletWidth = 768;
  static const double maxDesktopWidth = 1200;

  /// Check if the current screen is mobile size
  static bool isMobile(BuildContext context) {
    return MediaQuery.of(context).size.width < mobileBreakpoint;
  }

  /// Check if the current screen is tablet size
  static bool isTablet(BuildContext context) {
    final width = MediaQuery.of(context).size.width;
    return width >= mobileBreakpoint && width < tabletBreakpoint;
  }

  /// Check if the current screen is desktop size
  static bool isDesktop(BuildContext context) {
    return MediaQuery.of(context).size.width >= tabletBreakpoint;
  }

  /// Get responsive font size based on screen size
  static double fontSize(BuildContext context, double baseFontSize) {
    if (isMobile(context)) {
      return baseFontSize * 0.8; // Reduced from 0.9 to make smaller
    } else if (isTablet(context)) {
      return baseFontSize * 0.9; // Reduced from 1.0 to make smaller
    } else {
      return baseFontSize * 1.0; // Reduced from 1.1 to make smaller
    }
  }

  /// Get responsive spacing based on screen size
  static double spacing(BuildContext context, double baseSpacing) {
    if (isMobile(context)) {
      return baseSpacing * 0.8;
    } else if (isTablet(context)) {
      return baseSpacing;
    } else {
      return baseSpacing * 1.2;
    }
  }

  /// Get responsive padding based on screen size
  static EdgeInsets padding(BuildContext context, EdgeInsets basePadding) {
    final multiplier = isMobile(context) ? 0.8 : isTablet(context) ? 1.0 : 1.2;
    return EdgeInsets.only(
      left: basePadding.left * multiplier,
      top: basePadding.top * multiplier,
      right: basePadding.right * multiplier,
      bottom: basePadding.bottom * multiplier,
    );
  }

  /// Get maximum container width based on screen size
  static double maxWidth(BuildContext context) {
    if (isMobile(context)) {
      return maxMobileWidth;
    } else if (isTablet(context)) {
      return maxTabletWidth;
    } else {
      return maxDesktopWidth;
    }
  }

  /// Get responsive width percentage
  static double width(BuildContext context, double percentage) {
    return MediaQuery.of(context).size.width * percentage;
  }

  /// Get responsive height percentage
  static double height(BuildContext context, double percentage) {
    return MediaQuery.of(context).size.height * percentage;
  }

  /// Get responsive value based on screen size
  static T responsive<T>({
    required BuildContext context,
    required T mobile,
    T? tablet,
    T? desktop,
  }) {
    if (isMobile(context)) {
      return mobile;
    } else if (isTablet(context)) {
      return tablet ?? mobile;
    } else {
      return desktop ?? tablet ?? mobile;
    }
  }
}

/// A responsive container widget that automatically limits width based on screen size
class ResponsiveContainer extends StatelessWidget {
  final Widget child;
  final EdgeInsets? padding;
  final double? maxWidth;
  final bool centerContent;

  const ResponsiveContainer({
    super.key,
    required this.child,
    this.padding,
    this.maxWidth,
    this.centerContent = true,
  });

  @override
  Widget build(BuildContext context) {
    final containerMaxWidth = maxWidth ?? Responsive.maxWidth(context);
    final responsivePadding = padding ?? Responsive.padding(
      context,
      const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
    );

    Widget content = Container(
      width: double.infinity,
      constraints: BoxConstraints(maxWidth: containerMaxWidth),
      padding: responsivePadding,
      child: child,
    );

    if (centerContent) {
      content = Center(child: content);
    }

    return content;
  }
}