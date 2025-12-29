import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/utils/smooth_scroll_physics.dart';
import '../../../../core/utils/responsive.dart';
import '../../../../core/theme/theme_controller.dart';
import '../../../../shared/animations/smooth_animations.dart';
import '../../../tax_forms/data/services/t1_form_storage_service.dart';
import '../../../tax_forms/data/services/t2_form_storage_service.dart';
import '../../../auth/data/auth_api.dart';

class ProfilePage extends StatelessWidget {
  const ProfilePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        automaticallyImplyLeading: false,
      ),
      body: ResponsiveContainer(
        centerContent: false,
        padding: EdgeInsets.all(Responsive.responsive(
          context: context,
          mobile: AppDimensions.screenPadding,
          tablet: AppDimensions.screenPaddingLarge,
          desktop: AppDimensions.spacingXl,
        )),
        child: SingleChildScrollView(
          physics: const SmoothBouncingScrollPhysics(),
          child: Column(
          children: [
            SmoothAnimations.slideUp(
              child: _buildProfileHeader(),
            ),
            const SizedBox(height: 32),
            SmoothAnimations.slideUp(
              delay: const Duration(milliseconds: 200),
              child: _buildProfileOptions(context),
            ),
            // Extra bottom padding to account for bottom nav
            const SizedBox(height: 100),
          ],
        ),
        ),
      ),
    );
  }

  Widget _buildProfileHeader() {
    return FutureBuilder(
      future: _fetchUserProfile(),
      builder: (context, snapshot) {
        final isLoading = snapshot.connectionState == ConnectionState.waiting;
        final hasError = snapshot.hasError;
        final user = snapshot.data;

        final initials = user?.initials ?? (ThemeController.userName.value.isNotEmpty
            ? ThemeController.userName.value.trim().substring(0, 1).toUpperCase()
            : 'U');
        final fullName = user?.fullName ?? ThemeController.userName.value;
        final email = user?.email ?? '';

        return Container(
          width: double.infinity,
          padding: const EdgeInsets.all(AppDimensions.spacingLg),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            border: Border.all(color: Theme.of(context).dividerColor),
          ),
          child: Column(
            children: [
              CircleAvatar(
                radius: 40,
                backgroundColor: AppColors.primary.withValues(alpha: 0.1),
                child: Text(
                  initials,
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: AppColors.primary,
                  ),
                ),
              ),
              const SizedBox(height: 16),
              if (isLoading) const SizedBox(height: 4),
              Text(
                fullName,
                style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 4),
              if (isLoading)
                const SizedBox(
                  height: 16,
                  width: 16,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              else if (hasError)
                const Text(
                  'Could not load profile',
                  style: TextStyle(color: AppColors.grey600),
                )
              else
                Text(
                  email,
                  style: const TextStyle(
                    color: AppColors.grey600,
                  ),
                ),
            ],
          ),
        );
      },
    );
  }

  Future<UserProfile?> _fetchUserProfile() async {
    try {
      final profile = await AuthApi.getCurrentUser();
      // Update the global userName as well to keep Dashboard in sync
      await ThemeController.setUserName(profile.fullName);
      return profile;
    } catch (_) {
      return null;
    }
  }

  Widget _buildProfileOptions(BuildContext context) {
    final options = [
      {
        'icon': Icons.person_outline,
        'title': 'Edit Profile',
        'subtitle': 'Update your personal information',
        'onTap': () {},
      },
      {
        'icon': Icons.security_outlined,
        'title': 'Security',
        'subtitle': 'Change password and security settings',
        'onTap': () {},
      },
      {
        'icon': Icons.notifications_outlined,
        'title': 'Notifications',
        'subtitle': 'Manage notification preferences',
        'onTap': () {},
      },
      {
        'icon': Icons.help_outline,
        'title': 'Help & Support',
        'subtitle': 'Get help and contact support',
        'onTap': () => context.go('/help-support'),
      },
      {
        'icon': Icons.logout,
        'title': 'Sign Out',
        'subtitle': 'Sign out of your account',
        'onTap': () async {
          // Show confirmation dialog
          final shouldSignOut = await _showSignOutDialog(context);
          if (shouldSignOut == true && context.mounted) {
            await _performSignOut(context);
          }
        },
        'isDestructive': true,
      },
    ];

    return Container(
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        border: Border.all(color: Theme.of(context).dividerColor),
      ),
      child: ListView.separated(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: options.length,
        separatorBuilder: (context, index) => const Divider(height: 1),
        itemBuilder: (context, index) {
          final option = options[index];
          final isDestructive = option['isDestructive'] as bool? ?? false;
          return ListTile(
            leading: Icon(
              option['icon'] as IconData,
              color: isDestructive ? AppColors.error : AppColors.grey600,
            ),
            title: Text(
              option['title'] as String,
              style: TextStyle(
                fontWeight: FontWeight.w500,
                color: isDestructive ? AppColors.error : null,
              ),
            ),
            subtitle: Text(option['subtitle'] as String),
            trailing: const Icon(Icons.chevron_right),
            onTap: option['onTap'] as VoidCallback,
          );
        },
      ),
    );
  }

  Future<bool?> _showSignOutDialog(BuildContext context) {
    return showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        icon: const Icon(
          Icons.logout,
          color: AppColors.error,
          size: 48,
        ),
        title: const Text('Sign Out'),
        content: const Text(
          'Are you sure you want to sign out? This will clear all your saved forms data.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(false),
            child: const Text('Cancel'),
          ),
          ElevatedButton(
            onPressed: () => Navigator.of(context).pop(true),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.error,
              foregroundColor: AppColors.white,
            ),
            child: const Text('Sign Out'),
          ),
        ],
      ),
    );
  }

  Future<void> _performSignOut(BuildContext context) async {
    try {
      // Clear all forms data and auth state first
      await T1FormStorageService.instance.clearAllFormsData();
      await T2FormStorageService.instance.clearAllFormsData();
      await ThemeController.setLoggedIn(false);
      await ThemeController.setUserName('User');
      
      // Navigate to welcome page immediately
      if (context.mounted) {
        context.go('/welcome');
      }
    } catch (e) {
      // Show error message if something goes wrong
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Error signing out. Please try again.'),
            backgroundColor: AppColors.error,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }
    }
  }
}
