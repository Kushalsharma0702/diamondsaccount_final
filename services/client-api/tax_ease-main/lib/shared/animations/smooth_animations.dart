import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../core/constants/app_dimensions.dart';

/// Premium smooth animations for Tax Ease app
class SmoothAnimations {
  SmoothAnimations._();

  /// Custom page route with smooth slide transition
  static PageRouteBuilder<T> slidePageRoute<T>({
    required Widget page,
    Duration duration = const Duration(milliseconds: AppDimensions.animationDurationMedium),
    Offset beginOffset = const Offset(1.0, 0.0),
    Curve curve = Curves.easeInOutCubic,
  }) {
    return PageRouteBuilder<T>(
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        final slideAnimation = Tween(
          begin: beginOffset,
          end: Offset.zero,
        ).animate(CurvedAnimation(
          parent: animation,
          curve: curve,
        ));

        final fadeAnimation = Tween(
          begin: 0.0,
          end: 1.0,
        ).animate(CurvedAnimation(
          parent: animation,
          curve: const Interval(0.0, 0.5, curve: Curves.easeOut),
        ));

        return SlideTransition(
          position: slideAnimation,
          child: FadeTransition(
            opacity: fadeAnimation,
            child: child,
          ),
        );
      },
    );
  }

  /// Smooth scale and fade transition
  static PageRouteBuilder<T> scalePageRoute<T>({
    required Widget page,
    Duration duration = const Duration(milliseconds: AppDimensions.animationDurationMedium),
    double beginScale = 0.8,
    Curve curve = Curves.easeInOutCubic,
  }) {
    return PageRouteBuilder<T>(
      pageBuilder: (context, animation, secondaryAnimation) => page,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        final scaleAnimation = Tween(
          begin: beginScale,
          end: 1.0,
        ).animate(CurvedAnimation(
          parent: animation,
          curve: curve,
        ));

        final fadeAnimation = Tween(
          begin: 0.0,
          end: 1.0,
        ).animate(CurvedAnimation(
          parent: animation,
          curve: curve,
        ));

        return ScaleTransition(
          scale: scaleAnimation,
          child: FadeTransition(
            opacity: fadeAnimation,
            child: child,
          ),
        );
      },
    );
  }

  /// Smooth fade in animation widget
  static Widget fadeIn({
    required Widget child,
    Duration duration = const Duration(milliseconds: AppDimensions.animationDurationMedium),
    Duration delay = Duration.zero,
    Curve curve = Curves.easeInOut,
    Key? key,
  }) {
    return TweenAnimationBuilder<double>(
      key: key,
      duration: duration + delay,
      tween: Tween(begin: 0.0, end: 1.0),
      curve: curve,
      builder: (context, value, child) {
        return Opacity(
          opacity: delay.inMilliseconds > 0 
              ? (value > delay.inMilliseconds / (duration + delay).inMilliseconds ? 
                 (value - delay.inMilliseconds / (duration + delay).inMilliseconds) * 
                 ((duration + delay).inMilliseconds / duration.inMilliseconds) : 0.0)
              : value,
          child: child,
        );
      },
      child: child,
    );
  }

  /// Smooth slide up animation
  static Widget slideUp({
    required Widget child,
    Duration duration = const Duration(milliseconds: AppDimensions.animationDurationMedium),
    Duration delay = Duration.zero,
    double beginOffset = 20.0,
    Curve curve = Curves.easeOutCubic,
    Key? key,
  }) {
    return TweenAnimationBuilder<double>(
      key: key,
      duration: duration + delay,
      tween: Tween(begin: beginOffset, end: 0.0),
      curve: curve,
      builder: (context, value, child) {
        return Transform.translate(
          offset: Offset(0, value),
          child: Opacity(
            opacity: 1.0 - (value / beginOffset),
            child: child,
          ),
        );
      },
      child: child,
    );
  }

  /// Smooth scale animation
  static Widget scale({
    required Widget child,
    Duration duration = const Duration(milliseconds: AppDimensions.animationDurationMedium),
    Duration delay = Duration.zero,
    double beginScale = 0.8,
    Curve curve = Curves.elasticOut,
    Key? key,
  }) {
    return TweenAnimationBuilder<double>(
      key: key,
      duration: duration + delay,
      tween: Tween(begin: beginScale, end: 1.0),
      curve: curve,
      builder: (context, value, child) {
        return Transform.scale(
          scale: value,
          child: child,
        );
      },
      child: child,
    );
  }

  /// Staggered list animation
  static Widget staggeredList({
    required List<Widget> children,
    Duration staggerDelay = const Duration(milliseconds: 100),
    Duration animationDuration = const Duration(milliseconds: AppDimensions.animationDurationMedium),
    Curve curve = Curves.easeOutCubic,
  }) {
    return Column(
      children: children
          .asMap()
          .entries
          .map((entry) => slideUp(
                child: entry.value,
                duration: animationDuration,
                delay: Duration(milliseconds: entry.key * staggerDelay.inMilliseconds),
                curve: curve,
              ))
          .toList(),
    );
  }

  /// Ultra-luxury page transition as a CustomTransitionPage for go_router
  static CustomTransitionPage<T> ultraLuxuryPage<T>({
    required Widget child,
    Duration duration = const Duration(milliseconds: 420),
  }) {
    return CustomTransitionPage<T>(
      child: child,
      transitionDuration: duration,
      reverseTransitionDuration: duration,
      transitionsBuilder: (context, animation, secondaryAnimation, child) {
        final curve = CurvedAnimation(
          parent: animation,
          curve: Curves.easeInOutCubicEmphasized,
        );

        // Subtle parallax slide from the right + fade + gentle scale-in
        final slide = Tween<Offset>(
          begin: const Offset(0.06, 0.0),
          end: Offset.zero,
        ).animate(curve);

        final fade = Tween<double>(
          begin: 0.0,
          end: 1.0,
        ).animate(CurvedAnimation(
          parent: animation,
          curve: const Interval(0.0, 0.8, curve: Curves.easeOut),
        ));

        final scale = Tween<double>(
          begin: 0.98,
          end: 1.0,
        ).animate(curve);

        return FadeTransition(
          opacity: fade,
          child: SlideTransition(
            position: slide,
            child: ScaleTransition(
              scale: scale,
              child: child,
            ),
          ),
        );
      },
    );
  }

  /// Shimmer loading animation
  static Widget shimmer({
    required Widget child,
    Color baseColor = const Color(0xFFE0E0E0),
    Color highlightColor = const Color(0xFFF5F5F5),
    Duration duration = const Duration(milliseconds: 1500),
  }) {
    return TweenAnimationBuilder<double>(
      duration: duration,
      tween: Tween(begin: -2.0, end: 2.0),
      curve: Curves.easeInOut,
      builder: (context, value, child) {
        return ShaderMask(
          shaderCallback: (bounds) {
            return LinearGradient(
              begin: Alignment.centerLeft,
              end: Alignment.centerRight,
              colors: [
                baseColor,
                highlightColor,
                baseColor,
              ],
              stops: [
                (value - 1.0).clamp(0.0, 1.0),
                value.clamp(0.0, 1.0),
                (value + 1.0).clamp(0.0, 1.0),
              ],
            ).createShader(bounds);
          },
          child: child,
        );
      },
      child: child,
      onEnd: () {
        // Repeat the animation
        Future.delayed(const Duration(milliseconds: 500), () {
          // This would need a proper AnimationController for continuous repetition
        });
      },
    );
  }

  /// Smooth rotation animation
  static Widget rotate({
    required Widget child,
    Duration duration = const Duration(milliseconds: AppDimensions.animationDurationSlow),
    Curve curve = Curves.easeInOut,
  }) {
    return TweenAnimationBuilder<double>(
      duration: duration,
      tween: Tween(begin: 0.0, end: 1.0),
      curve: curve,
      builder: (context, value, child) {
        return Transform.rotate(
          angle: value * 2 * 3.14159, // Full rotation
          child: child,
        );
      },
      child: child,
    );
  }

  /// Elastic bounce animation
  static Widget bounce({
    required Widget child,
    Duration duration = const Duration(milliseconds: AppDimensions.animationDurationSlow),
    double minScale = 0.8,
  }) {
    return TweenAnimationBuilder<double>(
      duration: duration,
      tween: Tween(begin: minScale, end: 1.0),
      curve: Curves.elasticOut,
      builder: (context, value, child) {
        return Transform.scale(
          scale: value,
          child: child,
        );
      },
      child: child,
    );
  }

  /// Smooth progress indicator
  static Widget smoothProgress({
    required double value,
    Color? backgroundColor,
    Color? valueColor,
    Duration duration = const Duration(milliseconds: AppDimensions.animationDurationMedium),
  }) {
    return TweenAnimationBuilder<double>(
      duration: duration,
      tween: Tween(begin: 0.0, end: value),
      curve: Curves.easeInOut,
      builder: (context, animatedValue, child) {
        return LinearProgressIndicator(
          value: animatedValue,
          backgroundColor: backgroundColor,
          valueColor: valueColor != null 
              ? AlwaysStoppedAnimation<Color>(valueColor) 
              : null,
        );
      },
    );
  }
}
