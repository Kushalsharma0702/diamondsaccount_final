import 'package:flutter/material.dart';
import '../constants/app_text_styles.dart';

/// Example usage of the new typography system
/// This file demonstrates how to use the comprehensive font scheme
class TypographyUsageExample extends StatelessWidget {
  const TypographyUsageExample({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'Typography Showcase',
          style: AppTextStyles.appBarTitle,
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // ===== HEADINGS =====
            _buildSection('Headings', [
              _buildTextExample('H1 X-Large (84px)', AppTextStyles.h1XLarge),
              _buildTextExample('H1 Large (72px)', AppTextStyles.h1Large),
              _buildTextExample('H2 X-Large (72px)', AppTextStyles.h2XLarge),
              _buildTextExample('H2 Large (64px)', AppTextStyles.h2Large),
              _buildTextExample('H2 Medium (57.92px)', AppTextStyles.h2Medium),
              _buildTextExample('H2 Small (30px)', AppTextStyles.h2Small),
              _buildTextExample('H3 Large (64px)', AppTextStyles.h3Large),
              _buildTextExample('H3 Medium (56px)', AppTextStyles.h3Medium),
              _buildTextExample('H3 Small (24px)', AppTextStyles.h3Small),
              _buildTextExample('H3 X-Small (18px)', AppTextStyles.h3XSmall),
              _buildTextExample('Large Title (36px)', AppTextStyles.largeTitle),
              _buildTextExample('Heading (24px)', AppTextStyles.heading),
            ]),

            const SizedBox(height: 32),

            // ===== BODY TEXT =====
            _buildSection('Body Text', [
              _buildTextExample('Body X-Large (24px)', AppTextStyles.bodyXLarge),
              _buildTextExample('Body Large (20px)', AppTextStyles.bodyLarge),
              _buildTextExample('Body Medium (18px)', AppTextStyles.bodyMedium),
              _buildTextExample('Body Small (16px)', AppTextStyles.bodySmall),
              _buildTextExample('Body X-Small (14px)', AppTextStyles.bodyXSmall),
              _buildTextExample('Large Body Expanded (18px)', AppTextStyles.largeBodyExpanded),
              _buildTextExample('Large Body (18px)', AppTextStyles.largeBody),
              _buildTextExample('Small Body (14px)', AppTextStyles.smallBody),
            ]),

            const SizedBox(height: 32),

            // ===== LINKS =====
            _buildSection('Links', [
              _buildTextExample('Link Large (24px)', AppTextStyles.linkLarge),
              _buildTextExample('Link Medium (20px)', AppTextStyles.linkMedium),
              _buildTextExample('Link (18px)', AppTextStyles.link),
              _buildTextExample('Link Small (16px)', AppTextStyles.linkSmall),
              _buildTextExample('Link X-Small (14px)', AppTextStyles.linkXSmall),
            ]),

            const SizedBox(height: 32),

            // ===== BUTTONS & LABELS =====
            _buildSection('Buttons & Labels', [
              _buildTextExample('Button (18px)', AppTextStyles.button),
              _buildTextExample('Button Small (16px)', AppTextStyles.buttonSmall),
              _buildTextExample('Label (18px)', AppTextStyles.label),
              _buildTextExample('Label Medium (14px)', AppTextStyles.labelMedium),
            ]),

            const SizedBox(height: 32),

            // ===== COLOR VARIATIONS =====
            _buildSection('Color Variations', [
              _buildTextExample('Primary Color', AppTextStyles.h3MediumPrimary),
              _buildTextExample('Secondary Color', AppTextStyles.h3MediumSecondary),
              _buildTextExample('Grey Color', AppTextStyles.bodyMediumGrey),
              _buildTextExample('Error Color', AppTextStyles.bodyMediumError),
              _buildTextExample('Success Color', AppTextStyles.bodyMediumSuccess),
            ]),

            const SizedBox(height: 32),

            // ===== COMMON COMBINATIONS =====
            _buildSection('Common UI Components', [
              _buildTextExample('App Bar Title', AppTextStyles.appBarTitle),
              _buildTextExample('Card Title', AppTextStyles.cardTitle),
              _buildTextExample('Card Subtitle', AppTextStyles.cardSubtitle),
              _buildTextExample('Form Label', AppTextStyles.formLabel),
              _buildTextExample('Form Error', AppTextStyles.formError),
              _buildTextExample('Navigation Item', AppTextStyles.navigationItem),
              _buildTextExample('Navigation Active', AppTextStyles.navigationItemActive),
              _buildTextExample('Tab Label', AppTextStyles.tabLabel),
              _buildTextExample('Tab Active', AppTextStyles.tabLabelActive),
              _buildTextExample('Chip Label', AppTextStyles.chipLabel),
              _buildTextExample('Badge Text', AppTextStyles.badgeText),
              _buildTextExample('Caption', AppTextStyles.caption),
              _buildTextExample('Overline', AppTextStyles.overline),
            ]),

            const SizedBox(height: 32),

            // ===== UTILITY EXAMPLES =====
            _buildSection('Utility Examples', [
              _buildTextExample('With Underline', AppTextStyles.withUnderline(AppTextStyles.link)),
              _buildTextExample('With Bold', AppTextStyles.withBold(AppTextStyles.bodyMedium)),
              _buildTextExample('With Semi-Bold', AppTextStyles.withSemiBold(AppTextStyles.bodyMedium)),
              _buildTextExample('With Medium', AppTextStyles.withMedium(AppTextStyles.bodyMedium)),
              _buildTextExample('With Opacity', AppTextStyles.withOpacity(AppTextStyles.bodyMedium, 0.7)),
            ]),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String title, List<Widget> examples) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: AppTextStyles.h3Small.copyWith(
            fontWeight: FontWeight.w700,
            decoration: TextDecoration.underline,
          ),
        ),
        const SizedBox(height: 16),
        ...examples,
      ],
    );
  }

  Widget _buildTextExample(String label, TextStyle style) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: AppTextStyles.caption,
          ),
          const SizedBox(height: 4),
          Text(
            'Sample text using $label style',
            style: style,
          ),
          const SizedBox(height: 4),
          Container(
            height: 1,
            color: Colors.grey.withOpacity(0.2),
          ),
        ],
      ),
    );
  }
}

/// How to use the typography system:
/// 
/// 1. **Direct usage with AppTextStyles:**
///    ```dart
///    Text('Heading', style: AppTextStyles.h2Large)
///    Text('Body text', style: AppTextStyles.bodyMedium)
///    Text('Link', style: AppTextStyles.link)
///    ```
/// 
/// 2. **With color variations:**
///    ```dart
///    Text('Primary heading', style: AppTextStyles.h2LargePrimary)
///    Text('Error message', style: AppTextStyles.bodyMediumError)
///    Text('Success message', style: AppTextStyles.linkSuccess)
///    ```
/// 
/// 3. **Using utility methods:**
///    ```dart
///    Text('Custom color', style: AppTextStyles.withColor(AppTextStyles.bodyMedium, Colors.purple))
///    Text('With opacity', style: AppTextStyles.withOpacity(AppTextStyles.bodyLarge, 0.8))
///    Text('Bold text', style: AppTextStyles.withBold(AppTextStyles.bodyMedium))
///    Text('Underlined link', style: AppTextStyles.withUnderline(AppTextStyles.link))
///    ```
/// 
/// 4. **Common UI components:**
///    ```dart
///    AppBar(title: Text('Title', style: AppTextStyles.appBarTitle))
///    Card(child: Text('Card title', style: AppTextStyles.cardTitle))
///    TextFormField(style: AppTextStyles.formInput)
///    Text('Error', style: AppTextStyles.formError)
///    ```
/// 
/// 5. **Using Flutter's Material TextTheme (automatically applied):**
///    ```dart
///    Text('Display Large', style: Theme.of(context).textTheme.displayLarge)
///    Text('Headline Medium', style: Theme.of(context).textTheme.headlineMedium)
///    Text('Body Large', style: Theme.of(context).textTheme.bodyLarge)
///    ```