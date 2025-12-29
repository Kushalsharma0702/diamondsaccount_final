import 'dart:io';
import 'dart:ui' as ui;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

/// Simple script to create a padded version of the logo for adaptive icons
/// This ensures the logo fits properly within the adaptive icon safe zone
void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Load the original logo
  final ByteData data = await rootBundle.load('assets/images/logos/logo.png');
  final Uint8List bytes = data.buffer.asUint8List();
  final ui.Codec codec = await ui.instantiateImageCodec(bytes);
  final ui.FrameInfo frame = await codec.getNextFrame();
  final ui.Image originalImage = frame.image;
  
  // Create a padded version (add 20% padding around the logo)
  const int finalSize = 512; // Standard icon size
  const double padding = 0.15; // 15% padding
  const double logoScale = 1.0 - (padding * 2);
  
  final ui.PictureRecorder recorder = ui.PictureRecorder();
  final Canvas canvas = Canvas(recorder);
  
  // Fill with transparent background
  canvas.drawRect(
    Rect.fromLTWH(0, 0, finalSize.toDouble(), finalSize.toDouble()),
    Paint()..color = Colors.transparent,
  );
  
  // Calculate logo size and position
  final double logoSize = finalSize * logoScale;
  final double offset = finalSize * padding;
  
  // Draw the logo centered with padding
  final Rect destRect = Rect.fromLTWH(offset, offset, logoSize, logoSize);
  final Rect srcRect = Rect.fromLTWH(0, 0, originalImage.width.toDouble(), originalImage.height.toDouble());
  
  canvas.drawImageRect(originalImage, srcRect, destRect, Paint());
  
  // Convert to image
  final ui.Picture picture = recorder.endRecording();
  final ui.Image paddedImage = await picture.toImage(finalSize, finalSize);
  
  // Convert to PNG bytes
  final ByteData? pngBytes = await paddedImage.toByteData(format: ui.ImageByteFormat.png);
  if (pngBytes != null) {
    final File outputFile = File('assets/images/logos/logo_padded.png');
    await outputFile.writeAsBytes(pngBytes.buffer.asUint8List());
    // Logo created successfully
  }
}