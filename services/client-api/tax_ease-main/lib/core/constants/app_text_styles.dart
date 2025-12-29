import 'package:flutter/material.dart';
import '../theme/app_typography.dart';
import 'app_colors.dart';

/// Pre-defined text styles for easy usage throughout the app
/// Based on the designer's font scheme with common color variations
class AppTextStyles {
  AppTextStyles._();

  // ===== HEADINGS =====
  
  /// H1 Styles - Tiempos Headline (Libre Baskerville)
  static TextStyle get h1XLarge => AppTypography.h1Large;
  static TextStyle get h1Large => AppTypography.h1Medium;
  
  /// H2 Styles
  static TextStyle get h2XLarge => AppTypography.h2Large;
  static TextStyle get h2Large => AppTypography.h2Medium;
  static TextStyle get h2Medium => AppTypography.h2Futura;
  static TextStyle get h2Small => AppTypography.h2FuturaSmall;
  
  /// H3 Styles
  static TextStyle get h3Large => AppTypography.h3Tiempos;
  static TextStyle get h3Medium => AppTypography.h3Futura;
  static TextStyle get h3Small => AppTypography.h3FuturaSmall;
  static TextStyle get h3XSmall => AppTypography.h3FuturaMini;
  
  /// Large Title
  static TextStyle get largeTitle => AppTypography.largeTitle;
  
  /// General Heading
  static TextStyle get heading => AppTypography.heading;

  // ===== BODY TEXT =====
  
  /// Body Text Variations
  static TextStyle get bodyXLarge => AppTypography.bodyLarge;
  static TextStyle get bodyLarge => AppTypography.bodyMedium;
  static TextStyle get bodyMedium => AppTypography.body;
  static TextStyle get bodySmall => AppTypography.bodySmall;
  static TextStyle get bodyXSmall => AppTypography.bodyXSmall;
  
  /// Large Body Text
  static TextStyle get largeBodyExpanded => AppTypography.largeBodyExpanded;
  static TextStyle get largeBody => AppTypography.largeBody;
  
  /// Small Body Text
  static TextStyle get smallBody => AppTypography.smallBody;

  // ===== LINKS =====
  
  /// Link Styles
  static TextStyle get linkLarge => AppTypography.linkLarge;
  static TextStyle get linkMedium => AppTypography.linkMedium;
  static TextStyle get link => AppTypography.link;
  static TextStyle get linkSmall => AppTypography.linkSmall;
  static TextStyle get linkXSmall => AppTypography.linkXSmall;

  // ===== BUTTONS =====
  
  /// Button Text Styles
  static TextStyle get button => AppTypography.button;
  static TextStyle get buttonSmall => AppTypography.buttonSmall;

  // ===== LABELS =====
  
  /// Label Styles
  static TextStyle get label => AppTypography.label;
  static TextStyle get labelMedium => AppTypography.labelMedium;

  // ===== COLOR VARIATIONS =====
  
  /// Primary Color Variations
  static TextStyle get h1XLargePrimary => h1XLarge.copyWith(color: AppColors.primary);
  static TextStyle get h2LargePrimary => h2Large.copyWith(color: AppColors.primary);
  static TextStyle get h3MediumPrimary => h3Medium.copyWith(color: AppColors.primary);
  static TextStyle get bodyMediumPrimary => bodyMedium.copyWith(color: AppColors.primary);
  static TextStyle get linkPrimary => link.copyWith(color: AppColors.primary);
  static TextStyle get buttonPrimary => button.copyWith(color: AppColors.primary);
  
  /// Secondary Color Variations
  static TextStyle get h2LargeSecondary => h2Large.copyWith(color: AppColors.secondary);
  static TextStyle get h3MediumSecondary => h3Medium.copyWith(color: AppColors.secondary);
  static TextStyle get bodyMediumSecondary => bodyMedium.copyWith(color: AppColors.secondary);
  static TextStyle get linkSecondary => link.copyWith(color: AppColors.secondary);
  
  /// White Color Variations (for dark backgrounds)
  static TextStyle get h1XLargeWhite => h1XLarge.copyWith(color: AppColors.white);
  static TextStyle get h2LargeWhite => h2Large.copyWith(color: AppColors.white);
  static TextStyle get h3MediumWhite => h3Medium.copyWith(color: AppColors.white);
  static TextStyle get bodyMediumWhite => bodyMedium.copyWith(color: AppColors.white);
  static TextStyle get linkWhite => link.copyWith(color: AppColors.white);
  static TextStyle get buttonWhite => button.copyWith(color: AppColors.white);
  
  /// Grey Color Variations
  static TextStyle get bodyMediumGrey => bodyMedium.copyWith(color: AppColors.grey600);
  static TextStyle get bodySmallGrey => bodySmall.copyWith(color: AppColors.grey500);
  static TextStyle get labelGrey => label.copyWith(color: AppColors.grey600);
  static TextStyle get linkGrey => link.copyWith(color: AppColors.grey600);
  
  /// Error Color Variations
  static TextStyle get bodyMediumError => bodyMedium.copyWith(color: AppColors.error);
  static TextStyle get linkError => link.copyWith(color: AppColors.error);
  static TextStyle get labelError => label.copyWith(color: AppColors.error);
  
  /// Success Color Variations
  static TextStyle get bodyMediumSuccess => bodyMedium.copyWith(color: AppColors.success);
  static TextStyle get linkSuccess => link.copyWith(color: AppColors.success);
  static TextStyle get labelSuccess => label.copyWith(color: AppColors.success);

  // ===== UTILITY METHODS =====
  
  /// Get any text style with custom color
  static TextStyle withColor(TextStyle style, Color color) {
    return AppTypography.withColor(style, color);
  }
  
  /// Get any text style with opacity
  static TextStyle withOpacity(TextStyle style, double opacity) {
    return AppTypography.withOpacity(style, opacity);
  }
  
  /// Get text style with underline (useful for links)
  static TextStyle withUnderline(TextStyle style) {
    return style.copyWith(decoration: TextDecoration.underline);
  }
  
  /// Get text style with bold weight
  static TextStyle withBold(TextStyle style) {
    return style.copyWith(fontWeight: FontWeight.bold);
  }
  
  /// Get text style with semi-bold weight
  static TextStyle withSemiBold(TextStyle style) {
    return style.copyWith(fontWeight: FontWeight.w600);
  }
  
  /// Get text style with medium weight
  static TextStyle withMedium(TextStyle style) {
    return style.copyWith(fontWeight: FontWeight.w500);
  }

  // ===== COMMON COMBINATIONS =====
  
  /// Common text styles for specific UI components
  
  /// App Bar Title
  static TextStyle get appBarTitle => h3Small.copyWith(fontWeight: FontWeight.w600);
  
  /// Card Title
  static TextStyle get cardTitle => h3XSmall.copyWith(fontWeight: FontWeight.w600);
  
  /// Card Subtitle
  static TextStyle get cardSubtitle => bodySmall.copyWith(color: AppColors.grey600);
  
  /// Form Label
  static TextStyle get formLabel => label.copyWith(color: AppColors.grey700);
  
  /// Form Input Text
  static TextStyle get formInput => bodyMedium;
  
  /// Form Error Text
  static TextStyle get formError => bodyXSmall.copyWith(color: AppColors.error);
  
  /// Form Help Text
  static TextStyle get formHelp => bodyXSmall.copyWith(color: AppColors.grey500);
  
  /// Navigation Item
  static TextStyle get navigationItem => labelMedium.copyWith(fontWeight: FontWeight.w500);
  
  /// Navigation Item Active
  static TextStyle get navigationItemActive => labelMedium.copyWith(
    fontWeight: FontWeight.w600, 
    color: AppColors.primary,
  );
  
  /// Tab Label
  static TextStyle get tabLabel => label.copyWith(fontWeight: FontWeight.w500);
  
  /// Tab Label Active
  static TextStyle get tabLabelActive => label.copyWith(
    fontWeight: FontWeight.w600,
    color: AppColors.primary,
  );
  
  /// Chip Label
  static TextStyle get chipLabel => bodySmall.copyWith(fontWeight: FontWeight.w500);
  
  /// Badge Text
  static TextStyle get badgeText => bodyXSmall.copyWith(
    fontWeight: FontWeight.w600,
    color: AppColors.white,
  );
  
  /// Caption Text
  static TextStyle get caption => bodyXSmall.copyWith(color: AppColors.grey500);
  
  /// Overline Text
  static TextStyle get overline => bodyXSmall.copyWith(
    fontWeight: FontWeight.w500,
    letterSpacing: 0.5,
    color: AppColors.grey600,
  );
}