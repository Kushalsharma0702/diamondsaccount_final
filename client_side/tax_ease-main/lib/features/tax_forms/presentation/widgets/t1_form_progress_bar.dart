import 'package:flutter/material.dart';
import '../../../../core/constants/app_colors.dart';

class T1FormProgressBar extends StatelessWidget {
  final int currentStep;
  final int totalSteps;
  final AnimationController controller;

  const T1FormProgressBar({
    super.key,
    required this.currentStep,
    required this.totalSteps,
    required this.controller,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 8,
      decoration: BoxDecoration(
        color: AppColors.grey200,
        borderRadius: BorderRadius.circular(4),
      ),
      child: AnimatedBuilder(
        animation: controller,
        builder: (context, child) {
          return LinearProgressIndicator(
            value: controller.value,
            backgroundColor: Colors.transparent,
            valueColor: AlwaysStoppedAnimation<Color>(AppColors.primary),
            minHeight: 8,
          );
        },
      ),
    );
  }
}