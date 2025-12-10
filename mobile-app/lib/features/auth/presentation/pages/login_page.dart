import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/utils/smooth_scroll_physics.dart';
import '../../../../core/utils/responsive.dart';
import '../../../../core/theme/theme_controller.dart';
import '../../../../shared/animations/smooth_animations.dart';
import '../../data/auth_api.dart';
import '../../data/otp_api_service.dart';
import '../../../../core/firebase/firebase_auth_service.dart';
import '../../../../core/firebase/google_sign_in_service.dart';
class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isPasswordVisible = false;
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/welcome'),
        ),
        title: const Text('Sign In'),
      ),
      body: SafeArea(
        child: ResponsiveContainer(
          padding: EdgeInsets.all(Responsive.responsive(
            context: context,
            mobile: AppDimensions.screenPadding,
            tablet: AppDimensions.screenPaddingLarge,
            desktop: AppDimensions.spacingXl,
          )),
          child: SingleChildScrollView(
            physics: const SmoothBouncingScrollPhysics(),
            child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: 20),

              // Welcome text
              SmoothAnimations.slideUp(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Welcome back!',
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        color: AppColors.grey800,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Sign in to continue with your tax filing',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 40),

              // Login form
              SmoothAnimations.slideUp(
                delay: const Duration(milliseconds: 200),
                child: Form(
                  key: _formKey,
                  child: Column(
                    children: [
                      // Email field
                      TextFormField(
                        controller: _emailController,
                        keyboardType: TextInputType.emailAddress,
                        decoration: const InputDecoration(
                          labelText: 'Email Address',
                          hintText: 'Enter your email',
                          prefixIcon: Icon(Icons.email_outlined),
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter your email';
                          }
                          if (!RegExp(r'^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$').hasMatch(value)) {
                            return 'Please enter a valid email';
                          }
                          return null;
                        },
                      ),

                      const SizedBox(height: 20),

                      // Password field
                      TextFormField(
                        controller: _passwordController,
                        obscureText: !_isPasswordVisible,
                        decoration: InputDecoration(
                          labelText: 'Password',
                          hintText: 'Enter your password',
                          prefixIcon: const Icon(Icons.lock_outline),
                          suffixIcon: IconButton(
                            icon: Icon(
                              _isPasswordVisible
                                  ? Icons.visibility_off_outlined
                                  : Icons.visibility_outlined,
                            ),
                            onPressed: () {
                              setState(() {
                                _isPasswordVisible = !_isPasswordVisible;
                              });
                            },
                          ),
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Please enter your password';
                          }
                          if (value.length < 6) {
                            return 'Password must be at least 6 characters';
                          }
                          return null;
                        },
                      ),

                      const SizedBox(height: 16),

                      // Forgot password link
                      Align(
                        alignment: Alignment.centerRight,
                        child: TextButton(
                          onPressed: () => context.go('/forgot-password'),
                          child: Text(
                            'Forgot Password?',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: AppColors.primary,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ),

                      const SizedBox(height: 32),

                      // Login button
                      SizedBox(
                        width: double.infinity,
                        height: 56,
                        child: ElevatedButton(
                          onPressed: _isLoading ? null : _handleLogin,
                          child: _isLoading
                              ? const SizedBox(
                                  height: 20,
                                  width: 20,
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2,
                                    valueColor: AlwaysStoppedAnimation<Color>(
                                      AppColors.white,
                                    ),
                                  ),
                                )
                              : const Text('Sign In'),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              const SizedBox(height: 40),

              // Divider
              SmoothAnimations.slideUp(
                delay: const Duration(milliseconds: 400),
                child: Row(
                  children: [
                    const Expanded(child: Divider()),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        'OR',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppColors.grey500,
                        ),
                      ),
                    ),
                    const Expanded(child: Divider()),
                  ],
                ),
              ),

              const SizedBox(height: 32),

              // Social login buttons
              SmoothAnimations.slideUp(
                delay: const Duration(milliseconds: 600),
                child: Column(
                  children: [
                    // Google sign in button (temporary for testing)
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: OutlinedButton.icon(
                        onPressed: _isLoading ? null : _handleGoogleSignIn,
                        icon: Icon(Icons.g_mobiledata, color: Colors.red[600]),
                        label: const Text('Continue with Google'),
                        style: OutlinedButton.styleFrom(
                          side: BorderSide(color: AppColors.grey300),
                        ),
                      ),
                    ),
                    
                    // Temporary test button for direct Google Sign-In testing
                    const SizedBox(height: 16),
                    SizedBox(
                      width: double.infinity,
                      height: 56,
                      child: ElevatedButton(
                        onPressed: _isLoading ? null : () async {
                          final navigator = Navigator.of(context);
                          try {
                            final result = await GoogleSignInService.signInWithGoogle();
                            print("Google login user: ${result?.email}");
                            if (result != null) {
                              print("Google login ID token: ${result.idToken?.substring(0, 50)}...");
                            }
                            if (mounted) {
                              ScaffoldMessenger.of(navigator.context).showSnackBar(
                                SnackBar(
                                  content: Text(result != null 
                                    ? 'Google login user: ${result.email}' 
                                    : 'Google Sign-In was cancelled'),
                                  behavior: SnackBarBehavior.floating,
                                ),
                              );
                            }
                          } catch (e) {
                            print("Error: $e");
                            if (mounted) {
                              ScaffoldMessenger.of(navigator.context).showSnackBar(
                                SnackBar(
                                  content: Text('Error: $e'),
                                  backgroundColor: AppColors.error,
                                  behavior: SnackBarBehavior.floating,
                                ),
                              );
                            }
                          }
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.blue,
                        ),
                        child: const Text("Login with Google (Test)"),
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 40),

              // Sign up link
              SmoothAnimations.slideUp(
                delay: const Duration(milliseconds: 800),
                child: Center(
                  child: RichText(
                    text: TextSpan(
                      text: "Don't have an account? ",
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.grey600,
                      ),
                      children: [
                        WidgetSpan(
                          child: GestureDetector(
                            onTap: () => context.go('/signup'),
                            child: Text(
                              'Sign Up',
                              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                                color: AppColors.primary,
                                fontWeight: FontWeight.w600,
                                decoration: TextDecoration.underline,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 20),
            ],
          ),
        ),
        ),
      ),
    );
  }

  Future<void> _handleLogin() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final email = _emailController.text.trim();
      final password = _passwordController.text;

      // STEP 1: Authenticate with Firebase first
      // This gives us Firebase ID token which we'll use for OTP flow
      final firebaseResult = await FirebaseAuthService.loginWithEmail(
        email: email,
        password: password,
      );

      if (firebaseResult.idToken == null) {
        throw Exception('Failed to get Firebase ID token');
      }

      // STEP 2: Request OTP from backend using Firebase token
      // Backend will verify Firebase token and send OTP via AWS SES
      await OtpApiService.requestOtpWithFirebase(
        firebaseIdToken: firebaseResult.idToken!,
        email: email,
      );

      if (!mounted) return;
      
      // STEP 3: Navigate to OTP verification screen with Firebase token
      // Pass Firebase token via route query parameters
      context.go(
        '/otp-verification?email=${Uri.encodeComponent(email)}&signup=false&firebase_token=${Uri.encodeComponent(firebaseResult.idToken!)}&is_login=true',
      );
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(e.toString().replaceFirst('Exception: ', '')),
          backgroundColor: AppColors.error,
          behavior: SnackBarBehavior.floating,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }

  Future<void> _handleGoogleSignIn() async {
    setState(() {
      _isLoading = true;
    });

    try {
      // Call Google Sign-In service
      final result = await GoogleSignInService.signInWithGoogle();
      
      if (result == null) {
        // User cancelled
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Google Sign-In was cancelled'),
            behavior: SnackBarBehavior.floating,
          ),
        );
        return;
      }

      // Debug print for testing
      print("Google login user: ${result.email}");
      print("Google login ID token: ${result.idToken?.substring(0, 50)}...");

      // If we have an ID token, try to exchange it for backend JWT
      // If backend Firebase is not configured, fall back to OTP flow
      if (result.idToken != null) {
        try {
          final authResult = await AuthApi.loginWithGoogle(
            firebaseIdToken: result.idToken!,
          );

          // Persist token if provided
          if (authResult.token != null && authResult.token!.isNotEmpty) {
            await ThemeController.setAuthToken(authResult.token);
            await ThemeController.setRefreshToken(authResult.refreshToken); // Store refresh token
          }

          // Update basic app state
          await ThemeController.setLoggedIn(true);
          await ThemeController.setUserName(result.displayName ?? result.email ?? 'User');
          
          if (!mounted) return;
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Google Sign-In successful!'),
              backgroundColor: AppColors.success,
              behavior: SnackBarBehavior.floating,
            ),
          );
          context.go('/home');
        } catch (e) {
          // Backend Firebase verification failed - use OTP flow instead
          final errorMsg = e.toString().toLowerCase();
          if (errorMsg.contains('firebase') && errorMsg.contains('not configured')) {
            // Firebase Admin SDK not configured - use OTP flow
            if (!mounted) return;
            
            try {
              // Request OTP using Firebase token
              await OtpApiService.requestOtpWithFirebase(
                firebaseIdToken: result.idToken!,
                email: result.email ?? '',
              );
              
              // Navigate to OTP verification screen
              context.go(
                '/otp-verification?email=${Uri.encodeComponent(result.email ?? '')}&signup=false&firebase_token=${Uri.encodeComponent(result.idToken!)}&is_login=true',
              );
            } catch (otpError) {
              if (!mounted) return;
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Please use email/password login with OTP instead. Error: ${otpError.toString()}'),
                  backgroundColor: AppColors.error,
                  behavior: SnackBarBehavior.floating,
                ),
              );
            }
          } else {
            // Other error
            if (!mounted) return;
            ScaffoldMessenger.of(context).showSnackBar(
              SnackBar(
                content: Text('Authentication failed: ${e.toString()}'),
                backgroundColor: AppColors.error,
                behavior: SnackBarBehavior.floating,
              ),
            );
          }
        }
      } else {
        // No ID token
        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Google Sign-In successful, but no ID token received'),
            backgroundColor: AppColors.error,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    } catch (e) {
      print("Google Sign-In error: $e");
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Google Sign-In failed: ${e.toString()}'),
          backgroundColor: AppColors.error,
          behavior: SnackBarBehavior.floating,
        ),
      );
    } finally {
      if (mounted) {
        setState(() {
          _isLoading = false;
        });
      }
    }
  }
}
