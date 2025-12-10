import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../shared/animations/smooth_animations.dart';
import '../../data/auth_api.dart';
import '../../data/otp_api_service.dart';
import '../../../../core/theme/theme_controller.dart';
import '../../../tax_forms/data/t1_form_sync_service.dart';

class OtpVerificationPage extends StatefulWidget {
  final String email;
  final bool isSignup;
  final String? firebaseIdToken; // Firebase ID token for Firebase-based OTP flow

  const OtpVerificationPage({
    super.key,
    required this.email,
    this.isSignup = false,
    this.firebaseIdToken,
  });

  @override
  State<OtpVerificationPage> createState() => _OtpVerificationPageState();
}

class _OtpVerificationPageState extends State<OtpVerificationPage> {
  final List<TextEditingController> _otpControllers = List.generate(6, (index) => TextEditingController());
  final List<FocusNode> _otpFocusNodes = List.generate(6, (index) => FocusNode());
  bool _isLoading = false;
  bool _isResending = false;
  int _resendTimer = 60;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _startResendTimer();
  }

  @override
  void dispose() {
    for (var controller in _otpControllers) {
      controller.dispose();
    }
    for (var focusNode in _otpFocusNodes) {
      focusNode.dispose();
    }
    _timer?.cancel();
    super.dispose();
  }
  
  /// Sync locally saved forms to backend after successful login
  /// This ensures forms saved while offline are submitted to the database
  Future<void> _syncLocalFormsToBackend() async {
    try {
      // Run sync in background without blocking UI
      Future.microtask(() async {
        try {
          final result = await T1FormSyncService.syncAllFormsToBackend();
          if (result.syncedForms > 0) {
            debugPrint('✅ Auto-synced ${result.syncedForms} form(s) to backend');
            // Optionally show a snackbar if we're still on this page
            if (mounted) {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  content: Text('Synced ${result.syncedForms} form(s) to server'),
                  backgroundColor: AppColors.success,
                  behavior: SnackBarBehavior.floating,
                  duration: const Duration(seconds: 2),
                ),
              );
            }
          }
        } catch (e) {
          debugPrint('⚠️ Auto-sync failed: $e');
          // Don't show error to user - sync can be retried manually
        }
      });
    } catch (e) {
      debugPrint('⚠️ Failed to initiate form sync: $e');
    }
  }

  void _startResendTimer() {
    _timer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_resendTimer > 0) {
        setState(() {
          _resendTimer--;
        });
      } else {
        timer.cancel();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Verify Email'),
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(AppDimensions.screenPadding),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 40),

              // Icon
              SmoothAnimations.slideUp(
                child: Container(
                  width: 80,
                  height: 80,
                  decoration: BoxDecoration(
              color: AppColors.primary.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(40),
                  ),
                  child: const Icon(
                    Icons.mark_email_read_outlined,
                    size: 40,
                    color: AppColors.primary,
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // Title and description
              SmoothAnimations.slideUp(
                delay: const Duration(milliseconds: 200),
                child: Column(
                  children: [
                    Text(
                      'Verification Code',
                      style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        color: AppColors.grey800,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    Text(
                      'We\'ve sent a 6-digit verification code to',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.grey600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.email,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.primary,
                        fontWeight: FontWeight.w600,
                      ),
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 40),

              // OTP Input
              SmoothAnimations.slideUp(
                delay: const Duration(milliseconds: 400),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: List.generate(6, (index) => _buildOtpField(index)),
                ),
              ),

              const SizedBox(height: 40),

              // Verify button
              SmoothAnimations.slideUp(
                delay: const Duration(milliseconds: 600),
                child: SizedBox(
                  width: double.infinity,
                  height: 56,
                  child: ElevatedButton(
                    onPressed: _isLoading ? null : _handleVerifyOtp,
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
                        : const Text('Verify & Continue'),
                  ),
                ),
              ),

              const SizedBox(height: 32),

              // Resend code
              SmoothAnimations.slideUp(
                delay: const Duration(milliseconds: 800),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      'Didn\'t receive the code? ',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                    if (_resendTimer > 0)
                      Text(
                        'Resend in ${_resendTimer}s',
                        style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: AppColors.grey500,
                        ),
                      )
                    else
                      GestureDetector(
                        onTap: _isResending ? null : _handleResendCode,
                        child: Text(
                          _isResending ? 'Sending...' : 'Resend Code',
                          style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppColors.primary,
                            fontWeight: FontWeight.w600,
                            decoration: TextDecoration.underline,
                          ),
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildOtpField(int index) {
    return SizedBox(
      width: 45,
      height: 56,
      child: TextFormField(
        controller: _otpControllers[index],
        focusNode: _otpFocusNodes[index],
        keyboardType: TextInputType.number,
        textAlign: TextAlign.center,
        maxLength: 1,
        style: Theme.of(context).textTheme.titleLarge?.copyWith(
          fontWeight: FontWeight.w600,
        ),
        decoration: InputDecoration(
          counterText: '',
          contentPadding: const EdgeInsets.all(0),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
        inputFormatters: [FilteringTextInputFormatter.digitsOnly],
        onChanged: (value) {
          if (value.isNotEmpty) {
            if (index < 5) {
              _otpFocusNodes[index + 1].requestFocus();
            } else {
              _otpFocusNodes[index].unfocus();
            }
          } else if (value.isEmpty && index > 0) {
            _otpFocusNodes[index - 1].requestFocus();
          }
        },
      ),
    );
  }

  String _getOtpCode() {
    return _otpControllers.map((controller) => controller.text).join();
  }

  Future<void> _handleVerifyOtp() async {
    final otpCode = _getOtpCode();
    if (otpCode.length != 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Please enter the complete OTP code'),
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    setState(() {
      _isLoading = true;
    });

    try {
      // Check if this is Firebase-based OTP flow
      if (widget.firebaseIdToken != null && widget.firebaseIdToken!.isNotEmpty) {
        // Firebase-based flow: Verify OTP and get backend JWT token with refresh token
        final authResult = await OtpApiService.verifyOtpWithFirebase(
          email: widget.email.trim(),
          otpCode: otpCode,
          purpose: widget.isSignup ? 'email_verification' : 'login',
          firebaseIdToken: widget.firebaseIdToken!,
        );

        // Save backend JWT token and refresh token to SharedPreferences
        await ThemeController.setAuthToken(authResult.token);
        if (authResult.refreshToken != null) {
          await ThemeController.setRefreshToken(authResult.refreshToken);
        }
        await ThemeController.setLoggedIn(true);
        await ThemeController.setUserName(authResult.displayName ?? widget.email.split('@').first);

        // Auto-sync locally saved forms to backend after successful login
        _syncLocalFormsToBackend();

        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Login successful! Welcome back.'),
            backgroundColor: AppColors.success,
            behavior: SnackBarBehavior.floating,
          ),
        );

        // Navigate to dashboard
        context.go('/home');
      } else {
        // Traditional flow: Just verify OTP (for signup)
        await AuthApi.verifyOtp(
          email: widget.email.trim(),
          code: otpCode,
          purpose: 'email_verification',
        );

        if (!mounted) return;
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text(widget.isSignup ? 'Account verified successfully! Please sign in.' : 'Email verified successfully!'),
            backgroundColor: AppColors.success,
            behavior: SnackBarBehavior.floating,
          ),
        );

        // After verification, navigate to login to authenticate
        context.go('/login');
      }
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

  Future<void> _handleResendCode() async {
    setState(() {
      _isResending = true;
    });

    try {
      // Check if this is Firebase-based OTP flow
      if (widget.firebaseIdToken != null && widget.firebaseIdToken!.isNotEmpty) {
        // Firebase-based flow: Request OTP with Firebase token
        await OtpApiService.requestOtpWithFirebase(
          firebaseIdToken: widget.firebaseIdToken!,
          email: widget.email.trim(),
        );
      } else {
        // Traditional flow: Request OTP without Firebase token
        await AuthApi.requestOtp(
          email: widget.email.trim(),
          purpose: 'email_verification',
        );
      }

      if (!mounted) return;
      setState(() {
        _resendTimer = 60;
      });
      _startResendTimer();

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('Verification code sent successfully!'),
          behavior: SnackBarBehavior.floating,
        ),
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
          _isResending = false;
        });
      }
    }
  }
}
