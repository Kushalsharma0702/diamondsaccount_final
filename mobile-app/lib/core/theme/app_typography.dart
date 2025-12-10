import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

/// Comprehensive typography system for Tax Ease app
/// Based on designer's font scheme with Tiempos Headline and Futura PT
class AppTypography {
  AppTypography._();

  // Font families
  static const String tiemposHeadline = 'Tiempos Headline';
  static const String futuraPt = 'Futura PT';

  /// Headings (H1 - Large)
  static TextStyle get h1Large => GoogleFonts.getFont(
        'Libre Baskerville', // Closest available to Tiempos Headline
        fontSize: 72,
        fontWeight: FontWeight.w400,
        height: 83.52 / 72, // line-height / font-size
      );

  static TextStyle get h1Medium => GoogleFonts.getFont(
        'Libre Baskerville',
        fontSize: 64,
        fontWeight: FontWeight.w400,
        height: 74.24 / 64,
      );

  /// H2 Styles
  static TextStyle get h2Large => GoogleFonts.getFont(
        'Libre Baskerville',
        fontSize: 64,
        fontWeight: FontWeight.w400,
        height: 74.24 / 64,
      );

  static TextStyle get h2Medium => GoogleFonts.getFont(
        'Libre Baskerville',
        fontSize: 56,
        fontWeight: FontWeight.w400,
        height: 64.96 / 56,
      );

  static TextStyle get h2Futura => GoogleFonts.getFont(
        'Montserrat', // Closest available to Futura PT
        fontSize: 48,
        fontWeight: FontWeight.w400,
        height: 48 / 48,
      );

  static TextStyle get h2FuturaSmall => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 24,
        fontWeight: FontWeight.w500,
        height: 29.76 / 24,
      );

  /// H3 Styles
  static TextStyle get h3Tiempos => GoogleFonts.getFont(
        'Libre Baskerville',
        fontSize: 56,
        fontWeight: FontWeight.w400,
        height: 64.96 / 56,
      );

  static TextStyle get h3Futura => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 48,
        fontWeight: FontWeight.w500,
        height: 55.68 / 48,
      );

  static TextStyle get h3FuturaSmall => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 20,
        fontWeight: FontWeight.w500,
        height: 24.80 / 20,
      );

  static TextStyle get h3FuturaMini => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 16,
        fontWeight: FontWeight.w500,
        height: 19.84 / 16,
      );

  /// Large Title
  static TextStyle get largeTitle => GoogleFonts.getFont(
        'Libre Baskerville',
        fontSize: 30,
        fontWeight: FontWeight.w400,
        height: 34.80 / 30,
      );

  /// Heading Styles
  static TextStyle get heading => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 20,
        fontWeight: FontWeight.w400,
        height: 24.80 / 20,
      );

  /// Body Text Styles
  static TextStyle get bodyLarge => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 20,
        fontWeight: FontWeight.w400,
        height: 24.80 / 20,
      );

  static TextStyle get bodyMedium => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 18,
        fontWeight: FontWeight.w400,
        height: 22.32 / 18,
      );

  static TextStyle get body => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 16,
        fontWeight: FontWeight.w400,
        height: 19.84 / 16,
      );

  static TextStyle get bodySmall => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 14,
        fontWeight: FontWeight.w400,
        height: 17.36 / 14,
      );

  static TextStyle get bodyXSmall => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 12,
        fontWeight: FontWeight.w400,
        height: 14.88 / 12,
      );

  /// Large Body Text Styles
  static TextStyle get largeBodyExpanded => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 16,
        fontWeight: FontWeight.w400,
        height: 22.40 / 16,
      );

  static TextStyle get largeBody => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 16,
        fontWeight: FontWeight.w400,
        height: 19.84 / 16,
      );

  /// Small Body Text
  static TextStyle get smallBody => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 12,
        fontWeight: FontWeight.w400,
        height: 14.88 / 12,
      );

  /// Link Styles
  static TextStyle get linkLarge => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 20,
        fontWeight: FontWeight.w400,
        height: 24.80 / 20,
      );

  static TextStyle get linkMedium => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 18,
        fontWeight: FontWeight.w400,
        height: 22.32 / 18,
      );

  static TextStyle get link => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 16,
        fontWeight: FontWeight.w500,
        height: 19.84 / 16,
      );

  static TextStyle get linkSmall => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 14,
        fontWeight: FontWeight.w400,
        height: 17.36 / 14,
      );

  static TextStyle get linkXSmall => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 12,
        fontWeight: FontWeight.w400,
        height: 14.88 / 12,
      );

  /// Button Styles
  static TextStyle get button => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 16,
        fontWeight: FontWeight.w500,
        height: 19.84 / 16,
      );

  static TextStyle get buttonSmall => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 14,
        fontWeight: FontWeight.w500,
        height: 17.36 / 14,
      );

  /// Label Styles
  static TextStyle get label => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 16,
        fontWeight: FontWeight.w500,
        height: 18.56 / 16,
      );

  static TextStyle get labelMedium => GoogleFonts.getFont(
        'Montserrat',
        fontSize: 12,
        fontWeight: FontWeight.w500,
        height: 14.88 / 12,
      );

  /// Flutter Material Text Theme mapping
  /// Maps the custom typography to Flutter's TextTheme for consistent usage
  static TextTheme buildTextTheme(Brightness brightness, {Color? baseColor}) {
    final textColor = baseColor ?? 
        (brightness == Brightness.light ? const Color(0xFF424242) : const Color(0xFFFFFFFF));

    return TextTheme(
      // Display styles (largest headings)
      displayLarge: h1Large.copyWith(color: textColor),
      displayMedium: h1Medium.copyWith(color: textColor),
      displaySmall: h2Large.copyWith(color: textColor),

      // Headline styles
      headlineLarge: h2Medium.copyWith(color: textColor),
      headlineMedium: largeTitle.copyWith(color: textColor),
      headlineSmall: heading.copyWith(color: textColor),

      // Title styles
      titleLarge: h3FuturaSmall.copyWith(color: textColor),
      titleMedium: body.copyWith(color: textColor),
      titleSmall: bodySmall.copyWith(color: textColor),

      // Body styles (most common text)
      bodyLarge: bodyMedium.copyWith(color: textColor),
      bodyMedium: body.copyWith(color: textColor),
      bodySmall: bodyXSmall.copyWith(color: textColor),

      // Label styles (for buttons, chips, etc.)
      labelLarge: button.copyWith(color: textColor),
      labelMedium: label.copyWith(color: textColor),
      labelSmall: labelMedium.copyWith(color: textColor),
    );
  }

  /// Get text style with custom color
  static TextStyle withColor(TextStyle style, Color color) {
    return style.copyWith(color: color);
  }

  /// Get text style with custom opacity
  static TextStyle withOpacity(TextStyle style, double opacity) {
    return style.copyWith(color: style.color?.withValues(alpha: opacity));
  }
}