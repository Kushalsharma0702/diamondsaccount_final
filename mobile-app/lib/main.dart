import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:firebase_core/firebase_core.dart';
import 'firebase_options.dart'; // Generated file from FlutterFire CLI
import 'core/theme/app_theme.dart';
import 'core/constants/app_colors.dart';
import 'core/router/app_router.dart';
import 'core/theme/theme_controller.dart';
import 'core/firebase/firebase_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // Initialize Firebase (required for Firebase Auth to work)
  // If firebase_options.dart is not generated, this will throw an error
  // Run: flutterfire configure --project=taxease-ec35f to generate it
  // 
  // IMPORTANT: Firebase initialization is OPTIONAL.
  // If Firebase initialization fails, the app will continue with
  // existing AWS Cognito/SES OTP authentication only.
  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
    // Also initialize our Firebase service wrapper
    // This sets up service instances and should be called after Firebase.initializeApp()
    await FirebaseService.initialize();
    debugPrint('✅ Firebase initialized successfully');
  } catch (e) {
    // If Firebase is not configured, the app can still work with Cognito/SES
    // but Firebase Auth features will not be available
    // This is intentional - we support dual authentication methods
    debugPrint('⚠️ Firebase initialization failed: $e');
    debugPrint('ℹ️ App will continue with Cognito/SES authentication only');
    debugPrint('ℹ️ Firebase features will be disabled until Firebase is configured');
  }
  
  // Initialize theme controller and auth state
  // This is required for app functionality and is independent of Firebase
  await ThemeController.initialize();
  
  // Set preferred orientations
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
  ]);
  
  // Set system UI overlay style for premium look
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.dark,
    statusBarBrightness: Brightness.light,
    systemNavigationBarColor: AppColors.white,
    systemNavigationBarIconBrightness: Brightness.dark,
  ));
  
  runApp(const TaxEaseApp());
}

class TaxEaseApp extends StatelessWidget {
  const TaxEaseApp({super.key});

  @override
  Widget build(BuildContext context) {
    return ValueListenableBuilder<ThemeMode>(
      valueListenable: ThemeController.themeMode,
      builder: (context, mode, _) {
        return MaterialApp.router(
          title: 'TaxEase',
          debugShowCheckedModeBanner: false,
          theme: AppTheme.lightTheme,
          darkTheme: AppTheme.darkTheme,
          themeMode: mode,
          routerConfig: AppRouter.router,
        );
      },
    );
  }
}

