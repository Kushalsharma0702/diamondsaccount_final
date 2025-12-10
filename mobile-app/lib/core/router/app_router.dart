import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

// Import all pages
import '../../features/auth/presentation/pages/login_page.dart';
import '../../features/auth/presentation/pages/signup_page.dart';
import '../../features/auth/presentation/pages/forgot_password_page.dart';
import '../../features/auth/presentation/pages/otp_verification_page.dart';
import '../../features/onboarding/presentation/pages/onboarding_page.dart';
import '../../features/onboarding/presentation/pages/welcome_page.dart';
import '../../features/dashboard/presentation/pages/dashboard_page.dart';
import '../../features/tax_forms/presentation/pages/personal_tax_form_page.dart';
import '../../features/tax_forms/presentation/pages/business_tax_form_page.dart';
import '../../features/tax_forms/presentation/pages/form_review_page.dart';
import '../../features/tax_forms/presentation/pages/filled_forms_page.dart'; // YourFormsPage
import '../../features/documents/presentation/pages/documents_page.dart';
import '../../features/documents/presentation/pages/upload_documents_page.dart';
import '../../features/filing/presentation/pages/filing_status_page.dart';
import '../../features/filing/presentation/pages/filing_summary_page.dart';
import '../../features/notifications/presentation/pages/notifications_page.dart';
import '../../features/profile/presentation/pages/profile_page.dart';
import '../../features/settings/presentation/pages/settings_page.dart';
import '../../features/settings/presentation/pages/help_support_page.dart';
import '../../features/settings/presentation/pages/about_page.dart';
import '../../features/settings/presentation/pages/privacy_policy_page.dart';
import '../../features/settings/presentation/pages/terms_conditions_page.dart';
import '../../shared/widgets/main_scaffold.dart';
import '../../shared/animations/smooth_animations.dart';
import '../theme/theme_controller.dart';

/// App router configuration using go_router
class AppRouter {
  static final _rootNavigatorKey = GlobalKey<NavigatorState>();
  static final _shellNavigatorKey = GlobalKey<NavigatorState>();

  static CustomTransitionPage<dynamic> _page(Widget child) =>
      SmoothAnimations.ultraLuxuryPage(child: child);

  static final GoRouter router = GoRouter(
    navigatorKey: _rootNavigatorKey,
    initialLocation: '/welcome',
    redirect: (context, state) {
      // Check if user is logged in and redirect accordingly
      final isLoggedIn = ThemeController.isLoggedIn.value;
      final hasAuthToken = ThemeController.authToken != null && ThemeController.authToken!.isNotEmpty;
      
      // If user has auth token, they should be considered logged in
      if (hasAuthToken && !isLoggedIn) {
        // Token exists but state is not synced - this shouldn't happen if initialize() is called
        // but we handle it here as a safety check
        ThemeController.setLoggedIn(true);
        return '/home';
      }
      
      final isWelcomeOrOnboarding = state.uri.path == '/welcome' || state.uri.path == '/onboarding';
      
      // If user is logged in (or has token) but on welcome/onboarding, redirect to home
      if ((isLoggedIn || hasAuthToken) && isWelcomeOrOnboarding) {
        return '/home';
      }
      
      // If user is not logged in (and has no token) but trying to access protected routes, redirect to welcome
      final protectedRoutes = ['/home', '/tax-forms', '/documents', '/profile'];
      final isProtectedRoute = protectedRoutes.any((route) => state.uri.path.startsWith(route));
      if (!isLoggedIn && !hasAuthToken && isProtectedRoute) {
        return '/welcome';
      }
      
      // No redirect needed
      return null;
    },
    routes: [
      // Welcome & Onboarding
      GoRoute(
        path: '/welcome',
        name: 'welcome',
        pageBuilder: (context, state) => _page(const WelcomePage()),
      ),
      GoRoute(
        path: '/onboarding',
        name: 'onboarding',
        pageBuilder: (context, state) => _page(const OnboardingPage()),
      ),

      // Authentication Routes
      GoRoute(
        path: '/login',
        name: 'login',
        pageBuilder: (context, state) => _page(const LoginPage()),
      ),
      GoRoute(
        path: '/signup',
        name: 'signup',
        pageBuilder: (context, state) => _page(const SignupPage()),
      ),
      GoRoute(
        path: '/forgot-password',
        name: 'forgot-password',
        pageBuilder: (context, state) => _page(const ForgotPasswordPage()),
      ),
      GoRoute(
        path: '/otp-verification',
        name: 'otp-verification',
        pageBuilder: (context, state) {
          final email = state.uri.queryParameters['email'] ?? '';
          final isSignup = state.uri.queryParameters['signup'] == 'true';
          final firebaseToken = state.uri.queryParameters['firebase_token'];
          return _page(OtpVerificationPage(
            email: email,
            isSignup: isSignup,
            firebaseIdToken: firebaseToken,
          ));
        },
      ),

      // Main App Shell with Bottom Navigation - Only 4 main screens
      ShellRoute(
        navigatorKey: _shellNavigatorKey,
        builder: (context, state, child) {
          return MainScaffold(
            currentPath: state.uri.path,
            child: child,
          );
        },
        routes: [
          // Dashboard/Home
          GoRoute(
            path: '/home',
            name: 'home',
            pageBuilder: (context, state) => _page(const DashboardPage()),
          ),

          // YourForms (was filled-forms, now main nav page)
          GoRoute(
            path: '/tax-forms/filled-forms',
            name: 'your-forms',
            pageBuilder: (context, state) {
              final shouldRefresh = state.uri.queryParameters['refresh'] == 'true';
              return _page(YourFormsPage(shouldRefresh: shouldRefresh));
            },
          ),

          // Documents (main page only)
          GoRoute(
            path: '/documents',
            name: 'documents',
            pageBuilder: (context, state) => _page(const DocumentsPage()),
          ),

          // Profile
          GoRoute(
            path: '/profile',
            name: 'profile',
            pageBuilder: (context, state) => _page(const ProfilePage()),
          ),
        ],
      ),

      // Full Screen Routes (outside main shell) - All other screens
      
      // Tax Form Sub-routes (full screen)
      GoRoute(
        path: '/tax-forms/personal',
        name: 'personal-tax-form',
        pageBuilder: (context, state) {
          final formId = state.uri.queryParameters['formId'];
          return _page(PersonalTaxFormPage(formId: formId));
        },
      ),
      GoRoute(
        path: '/tax-forms/business',
        name: 'business-tax-form',
        pageBuilder: (context, state) {
          final formId = state.uri.queryParameters['formId'];
          return _page(BusinessTaxFormPage(formId: formId));
        },
      ),
      GoRoute(
        path: '/tax-forms/review',
        name: 'form-review',
        pageBuilder: (context, state) {
          final formType = state.uri.queryParameters['type'] ?? 'personal';
          return _page(FormReviewPage(formType: formType));
        },
      ),

      // Document Sub-routes (full screen)
      GoRoute(
        path: '/documents/upload',
        name: 'upload-documents',
        pageBuilder: (context, state) => _page(const UploadDocumentsPage()),
      ),

      // Filing Routes (full screen)
      GoRoute(
        path: '/filing-status',
        name: 'filing-status',
        pageBuilder: (context, state) => _page(const FilingStatusPage()),
      ),
      GoRoute(
        path: '/filing-summary',
        name: 'filing-summary',
        pageBuilder: (context, state) {
          final filingId = state.uri.queryParameters['id'] ?? '';
          return _page(FilingSummaryPage(filingId: filingId));
        },
      ),

      // Notifications / Communication
      GoRoute(
        path: '/notifications',
        name: 'notifications',
        pageBuilder: (context, state) => _page(const NotificationsPage()),
      ),

      // Settings Routes (full screen)
      GoRoute(
        path: '/settings',
        name: 'settings',
        pageBuilder: (context, state) => _page(const SettingsPage()),
      ),
      GoRoute(
        path: '/help-support',
        name: 'help-support',
        pageBuilder: (context, state) => _page(const HelpSupportPage()),
      ),
      GoRoute(
        path: '/about',
        name: 'about',
        pageBuilder: (context, state) => _page(const AboutPage()),
      ),
      GoRoute(
        path: '/privacy-policy',
        name: 'privacy-policy',
        pageBuilder: (context, state) => _page(const PrivacyPolicyPage()),
      ),
      GoRoute(
        path: '/terms-conditions',
        name: 'terms-conditions',
        pageBuilder: (context, state) => _page(const TermsConditionsPage()),
      ),
    ],
    errorBuilder: (context, state) => Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.error_outline,
              size: 64,
              color: Colors.red,
            ),
            const SizedBox(height: 16),
            Text(
              'Page Not Found',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 8),
            Text(
              'The page you are looking for does not exist.',
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: () => context.go('/home'),
              child: const Text('Go Home'),
            ),
          ],
        ),
      ),
    ),
  );
}

/// Route names for easy access
class Routes {
  static const String welcome = '/welcome';
  static const String onboarding = '/onboarding';
  static const String login = '/login';
  static const String signup = '/signup';
  static const String forgotPassword = '/forgot-password';
  static const String otpVerification = '/otp-verification';
  static const String home = '/home';
  static const String filledForms = '/tax-forms/filled-forms';
  static const String personalTaxForm = '/tax-forms/personal';
  static const String businessTaxForm = '/tax-forms/business';
  static const String formReview = '/tax-forms/review';
  static const String documents = '/documents';
  static const String uploadDocuments = '/documents/upload';
  static const String profile = '/profile';
  static const String filingStatus = '/filing-status';
  static const String filingSummary = '/filing-summary';
  static const String settings = '/settings';
  static const String helpSupport = '/help-support';
  static const String about = '/about';
  static const String privacyPolicy = '/privacy-policy';
  static const String termsConditions = '/terms-conditions';
}
