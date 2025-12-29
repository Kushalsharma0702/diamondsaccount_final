import 'package:flutter/material.dart';

/// Custom scroll physics that provides a smooth bouncing effect
/// with improved user experience for all scrollable content
/// Matches the exact bounce intensity of the home screen
class SmoothBouncingScrollPhysics extends BouncingScrollPhysics {
  const SmoothBouncingScrollPhysics({super.parent});

  @override
  SmoothBouncingScrollPhysics applyTo(ScrollPhysics? ancestor) {
    return SmoothBouncingScrollPhysics(parent: buildParent(ancestor));
  }
}
