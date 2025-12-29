import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../shared/animations/smooth_animations.dart';
import '../../../../core/theme/theme_controller.dart';
import '../../../tax_forms/data/services/t1_form_storage_service.dart';
import '../../../tax_forms/data/services/t2_form_storage_service.dart';
import '../../../tax_forms/data/services/unified_form_service.dart';
import '../../../auth/data/auth_api.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key});

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> with AutomaticKeepAliveClientMixin, WidgetsBindingObserver {
  // Add unique keys to prevent GlobalKey duplication during rebuilds
  static const _welcomeKey = ValueKey('dashboard_welcome');
  static const _quickStatsKey = ValueKey('dashboard_quick_stats');
  static const _quickActionsKey = ValueKey('dashboard_quick_actions');
  static const _recentActivityKey = ValueKey('dashboard_recent_activity');
  static const _taxDeadlinesKey = ValueKey('dashboard_tax_deadlines');

  late ScrollController _scrollController;
  String? _userEmail;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _scrollController = ScrollController();
    WidgetsBinding.instance.addObserver(this);
    _ensureUserNameFromMe();
  }

  @override
  void dispose() {
    WidgetsBinding.instance.removeObserver(this);
    _scrollController.dispose();
    super.dispose();
  }
  
  @override
  void didChangeAppLifecycleState(AppLifecycleState state) {
    if (state == AppLifecycleState.resumed && mounted) {
      // Refresh the page when app comes back into focus
      setState(() {});
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Scaffold(
      appBar: AppBar(
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Image.asset(
              'assets/images/logos/logo.png',
              height: 28,
              width: 28,
            ),
            const SizedBox(width: 8),
            const Text('TaxEase'),
          ],
        ),
        automaticallyImplyLeading: false,
        centerTitle: false,
        actions: [
          // Theme toggle
          IconButton(
            tooltip: 'Toggle theme',
            icon: Icon(
              Theme.of(context).brightness == Brightness.dark
                  ? Icons.light_mode_outlined
                  : Icons.dark_mode_outlined,
            ),
            onPressed: () {
              // Toggle theme using the controller
              // If currently system, assume light based on platform brightness
              ThemeController.toggle();
            },
          ),
          IconButton(
icon: const Icon(Icons.notifications_outlined),
            onPressed: () => context.push('/notifications'),
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => context.go('/settings'),
          ),
        ],
      ),
      body: SingleChildScrollView(
        controller: _scrollController,
        physics: const BouncingScrollPhysics(
          parent: AlwaysScrollableScrollPhysics(),
        ),
        padding: const EdgeInsets.all(AppDimensions.screenPadding),
        child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Welcome section
                SmoothAnimations.slideUp(
                  key: _welcomeKey,
                  child: _buildWelcomeSection(),
                ),

                const SizedBox(height: 24),

                // Progress tracker (separate neutral card)
                SmoothAnimations.slideUp(
                  delay: const Duration(milliseconds: 150),
                  child: _buildProgressCard(),
                ),

                const SizedBox(height: 24),

                // Quick stats
                SmoothAnimations.slideUp(
                  key: _quickStatsKey,
                  delay: const Duration(milliseconds: 300),
                  child: _buildQuickStats(),
                ),

                const SizedBox(height: 24),

                // Quick actions
                SmoothAnimations.slideUp(
                  key: _quickActionsKey,
                  delay: const Duration(milliseconds: 400),
                  child: _buildQuickActions(),
                ),

                const SizedBox(height: 24),

                // Recent activity
                SmoothAnimations.slideUp(
                  key: _recentActivityKey,
                  delay: const Duration(milliseconds: 600),
                  child: _buildRecentActivity(),
                ),

                const SizedBox(height: 24),

                // Tax deadlines
                SmoothAnimations.slideUp(
                  key: _taxDeadlinesKey,
                  delay: const Duration(milliseconds: 800),
                  child: _buildTaxDeadlines(),
                ),
                
                // Extra bottom padding to account for bottom nav
                const SizedBox(height: 100),
              ],
            ),
      ),
    );
  }

  Widget _buildWelcomeSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(AppDimensions.spacingXl),
      decoration: BoxDecoration(
        gradient: AppColors.primaryGradient,
        borderRadius: BorderRadius.circular(AppDimensions.radius2xl),
        boxShadow: [
          BoxShadow(
            color: AppColors.primary.withValues(alpha: 0.3),
            blurRadius: 20,
            offset: const Offset(0, 8),
            spreadRadius: 0,
          ),
          BoxShadow(
            color: AppColors.accentLight.withValues(alpha: 0.1),
            blurRadius: 40,
            offset: const Offset(0, 20),
            spreadRadius: -5,
          ),
        ],
      ),
      child: Stack(
        children: [
          // Subtle decorative shapes using brand colors
          Positioned(
            top: -25,
            right: -25,
            child: _decorShape(
              size: 100,
              color: AppColors.accentLight.withValues(alpha: 0.12),
              shape: BoxShape.circle,
            ),
          ),
          Positioned(
            bottom: -20,
            left: -15,
            child: _decorShape(
              size: 80,
              color: AppColors.primaryLight.withValues(alpha: 0.08),
              shape: BoxShape.circle,
            ),
          ),

          // Main content
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: ValueListenableBuilder<String>(
                      valueListenable: ThemeController.userName,
                    builder: (context, name, _) {
                      final firstName = _firstName(name);
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Hello ${firstName.isEmpty ? 'there!' : firstName}',
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                              color: AppColors.white,
                              fontWeight: FontWeight.w700,
                              letterSpacing: -0.5,
                              height: 1.1,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'Let\'s make tax filing ease',
                            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                              color: AppColors.white.withValues(alpha: 0.75),
                              fontWeight: FontWeight.w400,
                            ),
                          ),
                        ],
                      );
                    },
                    ),
                  ),
                  const SizedBox(width: 16),
                  // Elegant avatar with brand colors
                  ValueListenableBuilder<String>(
                    valueListenable: ThemeController.userName,
                    builder: (context, name, _) {
                      final initials = _userInitials(name);
                      return Container(
                        width: 60,
                        height: 60,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topLeft,
                            end: Alignment.bottomRight,
                            colors: [
                              AppColors.white.withValues(alpha: 0.25),
                              AppColors.white.withValues(alpha: 0.15),
                            ],
                          ),
                          borderRadius: BorderRadius.circular(18),
                          border: Border.all(
                            color: AppColors.white.withValues(alpha: 0.2),
                            width: 1.5,
                          ),
                        ),
                        child: Center(
                          child: Text(
                            initials,
                            style: Theme.of(context).textTheme.titleLarge?.copyWith(
                              color: AppColors.white,
                              fontWeight: FontWeight.w700,
                              letterSpacing: 1,
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ],
              ),

              const SizedBox(height: 20),

              // Premium stats row
              Row(
                children: [
                  Expanded(
                    child: _buildMiniStat(
                      icon: Icons.event_available_rounded,
                      label: 'Due Date',
                      value: 'Apr 30',
                    ),
                  ),
                  const SizedBox(width: 12),
                  Container(
                    width: 1,
                    height: 30,
                    color: AppColors.white.withValues(alpha: 0.2),
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: _buildMiniStat(
                      icon: Icons.schedule_rounded,
                      label: 'Time Left',
                      value: _daysLeftToNextApril30() == 0
                          ? 'Due today'
                          : '${_daysLeftToNextApril30()} days',
                    ),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildMiniStat({
    required IconData icon,
    required String label,
    required String value,
  }) {
    return Column(
      children: [
        Icon(
          icon,
          color: AppColors.white.withValues(alpha: 0.9),
          size: 18,
        ),
        const SizedBox(height: 4),
        Text(
          value,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
            color: AppColors.white,
            fontWeight: FontWeight.w700,
          ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.labelSmall?.copyWith(
            color: AppColors.white.withValues(alpha: 0.75),
            fontWeight: FontWeight.w500,
          ),
        ),
      ],
    );
  }

  Widget _decorShape({
    required double size,
    required Color color,
    required BoxShape shape,
  }) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: shape,
        gradient: RadialGradient(
          colors: [color, color.withValues(alpha: 0.0)],
          stops: const [0.3, 1.0],
        ),
      ),
    );
  }

  int _daysLeftToNextApril30() {
    final now = DateTime.now();
    final currentYear = now.year;
    final april30ThisYear = DateTime(currentYear, 4, 30);
    // Normalize times to dates only
    final today = DateTime(now.year, now.month, now.day);
    final target = today.isAfter(april30ThisYear)
        ? DateTime(currentYear + 1, 4, 30)
        : april30ThisYear;
    final diff = target.difference(today).inDays;
    return diff.clamp(0, 366);
  }


  String _userInitials(String name) {
    final parts = name.trim().split(RegExp(r"\s+")).where((p) => p.isNotEmpty).toList();
    if (parts.isEmpty) return 'U';
    if (parts.length == 1) return parts.first.substring(0, 1).toUpperCase();
    return (parts.first.substring(0, 1) + parts.last.substring(0, 1)).toUpperCase();
  }

  String _firstName(String name) {
    final trimmed = name.trim();
    if (trimmed.isEmpty) return '';
    return trimmed.split(RegExp(r"\s+")).first;
  }

  Future<void> _ensureUserNameFromMe() async {
    try {
      // Only try if we seem logged in and have a token
      if (ThemeController.isLoggedIn.value && ThemeController.authToken != null) {
        final me = await AuthApi.getCurrentUser();
        await ThemeController.setUserName(me.fullName);
        if (mounted) setState(() => _userEmail = me.email);
      }
    } catch (_) {
      // ignore failures silently for the dashboard
    }
  }


  Widget _buildProgressCard() {
    return FutureBuilder<Map<String, dynamic>>(
      future: _getProgressStatus(),
      builder: (context, snapshot) {
        final progressData = snapshot.data ?? {
          'progress': 0.0,
          'progressText': 'Get Started',
          'isComplete': false,
        };
        
        final progress = progressData['progress'] as double;
        final progressText = progressData['progressText'] as String;
        final isComplete = progressData['isComplete'] as bool;
        
        return GestureDetector(
          onTap: () => _handleProgressCardTap(progressData),
          child: Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: Theme.of(context).dividerColor,
                width: 1,
              ),
              boxShadow: [
                BoxShadow(
                  color: AppColors.shadowLight,
                  blurRadius: 4,
                  offset: const Offset(0, 2),
                ),
              ],
            ),
            child: Row(
              children: [
                // Progress indicator
                SizedBox(
                  width: 40,
                  height: 40,
                  child: progress == 0.0
                      ? Container(
                          decoration: BoxDecoration(
                            color: AppColors.primary.withValues(alpha: 0.1),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Icon(
                            Icons.play_arrow,
                            color: AppColors.primary,
                            size: 20,
                          ),
                        )
                      : Stack(
                          children: [
                            CircularProgressIndicator(
                              value: progress,
                              backgroundColor: Theme.of(context).dividerColor,
                              valueColor: AlwaysStoppedAnimation<Color>(
                                isComplete ? AppColors.success : AppColors.primary,
                              ),
                              strokeWidth: 3,
                            ),
                            Center(
                              child: isComplete
                                  ? Icon(
                                      Icons.check,
                                      color: AppColors.success,
                                      size: 16,
                                    )
                                  : Text(
                                      '${(progress * 100).toInt()}%',
                                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                                        color: Theme.of(context).textTheme.bodySmall?.color,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                            ),
                          ],
                        ),
                ),
                const SizedBox(width: 12),
                // Progress text
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        progressData['formType'] != null 
                            ? '${progressData['formType']} Tax Form Progress'
                            : 'Tax Form Progress',
                        style: Theme.of(context).textTheme.titleSmall?.copyWith(
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        progressText,
                        style: Theme.of(context).textTheme.bodySmall?.copyWith(
                          color: isComplete ? AppColors.success : null,
                          fontWeight: isComplete ? FontWeight.w600 : null,
                        ),
                      ),
                    ],
                  ),
                ),
                // Arrow icon
                Icon(
                  Icons.arrow_forward_ios,
                  color: AppColors.grey500,
                  size: 16,
                ),
              ],
            ),
          ),
        );
      },
    );
  }
  
  Future<void> _handleProgressCardTap(Map<String, dynamic> progressData) async {
    try {
      // If there's a specific form ID and type in progress data, navigate to it
      if (progressData['formId'] != null && progressData['formType'] != null) {
        final formId = progressData['formId'] as String;
        final formType = progressData['formType'] as String;
        
        if (formType == 'T1') {
          context.go('/tax-forms/personal?formId=$formId');
        } else if (formType == 'T2') {
          context.go('/tax-forms/business?formId=$formId');
        } else {
          context.go('/tax-forms/filled-forms');
        }
        return;
      }
      
      // If no progress data, try to find most recent form from both services
      final t1Forms = await T1FormStorageService.instance.loadAllForms();
      final t2Forms = await T2FormStorageService.instance.loadAllForms();
      
      // If no forms exist, show the Your Forms page to let user choose
      if (t1Forms.isEmpty && t2Forms.isEmpty) {
        if (mounted) context.go('/tax-forms/filled-forms');
        return;
      }
      
      // Find the most recent draft from both types
      final allDrafts = [
        ...t1Forms.where((f) => f.status == 'draft').map((f) => {
          'id': f.id,
          'type': 'T1',
          'updatedAt': f.updatedAt ?? DateTime(0),
        }),
        ...t2Forms.where((f) => f.status == 'draft').map((f) => {
          'id': f.id,
          'type': 'T2', 
          'updatedAt': f.updatedAt ?? DateTime(0),
        }),
      ];
      
      if (allDrafts.isNotEmpty) {
        // Navigate to the most recent draft
        final mostRecent = allDrafts.reduce((a, b) => 
          (a['updatedAt'] as DateTime).isAfter(b['updatedAt'] as DateTime) ? a : b);
        
        if (mounted) {
          if (mostRecent['type'] == 'T1') {
            context.go('/tax-forms/personal?formId=${mostRecent['id']}');
          } else {
            context.go('/tax-forms/business?formId=${mostRecent['id']}');
          }
        }
      } else {
        // All forms are submitted, show the Your Forms page
        if (mounted) context.go('/tax-forms/filled-forms');
      }
    } catch (e) {
      // Fallback to Your Forms page
      if (mounted) context.go('/tax-forms/filled-forms');
    }
  }
  
  Future<void> _handlePersonalTaxTap() async {
    try {
      final forms = await T1FormStorageService.instance.loadAllForms();
      
      // Find the most recent draft form
      final draftForms = forms.where((f) => f.status == 'draft').toList();
      
      if (draftForms.isNotEmpty) {
        // Navigate to the most recent draft
        final mostRecentDraft = draftForms.reduce((a, b) => 
          (a.updatedAt ?? DateTime(0)).isAfter(b.updatedAt ?? DateTime(0)) ? a : b);
        if (mounted) context.go('/tax-forms/personal?formId=${mostRecentDraft.id}');
      } else {
        // Create a new form
        final newForm = T1FormStorageService.instance.createNewForm();
        if (mounted) context.go('/tax-forms/personal?formId=${newForm.id}');
      }
    } catch (e) {
      // Fallback to creating a new form
      final newForm = T1FormStorageService.instance.createNewForm();
      if (mounted) context.go('/tax-forms/personal?formId=${newForm.id}');
    }
  }

  Future<void> _handleT1NewFiling() async {
    // Always create a new T1 form
    final newForm = T1FormStorageService.instance.createNewForm();
    if (mounted) context.go('/tax-forms/personal?formId=${newForm.id}');
  }

  Future<void> _handleT2NewFiling() async {
    // Always create a new T2 form
    final newForm = T2FormStorageService.instance.createNewForm();
    if (mounted) context.go('/tax-forms/business?formId=${newForm.id}');
  }
  
  Future<Map<String, dynamic>> _getProgressStatus() async {
    try {
      return await UnifiedFormService.instance.getUnifiedProgressStatus();
    } catch (e) {
      return {
        'progress': 0.0,
        'progressText': 'Get Started',
        'formType': null,
        'isComplete': false,
      };
    }
  }
  
  Future<Map<String, dynamic>> _getFormCounts() async {
    try {
      return await UnifiedFormService.instance.getFormCounts();
    } catch (e) {
      return {
        'submitted': 0,
        'drafts': 0,
        't1Count': 0,
        't2Count': 0,
        'total': 0,
      };
    }
  }


  Widget _buildQuickStats() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Overview',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        FutureBuilder<Map<String, dynamic>>(
          future: _getFormCounts(),
          builder: (context, snapshot) {
            final formCounts = snapshot.data ?? {'submitted': 0, 'drafts': 0, 'total': 0};
            final submittedCount = formCounts['submitted'] ?? 0;
            final draftsCount = formCounts['drafts'] ?? 0;
            
            return Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    icon: Icons.description_outlined,
                    title: 'Forms Filed',
                    value: '$submittedCount',
                    subtitle: 'This year',
                    color: AppColors.success,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: _buildStatCard(
                    icon: Icons.pending_outlined,
                    title: 'In Progress',
                    value: '$draftsCount',
                    subtitle: 'Draft saved',
                    color: AppColors.warning,
                  ),
                ),
              ],
            );
          },
        ),
      ],
    );
  }

  Widget _buildStatCard({
    required IconData icon,
    required String title,
    required String value,
    required String subtitle,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.all(AppDimensions.spacingMd),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
        border: Border.all(color: Theme.of(context).dividerColor),
        boxShadow: [
          BoxShadow(
            color: AppColors.shadowLight,
            blurRadius: 4,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: color, size: 24),
              const SizedBox(width: 8),
              Text(
                title,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  color: AppColors.grey600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            value,
            style: Theme.of(context).textTheme.headlineMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            subtitle,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              color: AppColors.grey500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Quick Actions',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        // Use Wrap in a LayoutBuilder to avoid GridView rounding overflow issues
        LayoutBuilder(
          builder: (context, constraints) {
            const spacing = 16.0;
            final availableWidth = constraints.maxWidth;
            final itemWidth = availableWidth > spacing ? (availableWidth - spacing) / 2 : availableWidth / 2;
            
            // Ensure we have positive width
            if (itemWidth <= 0 || availableWidth <= 0) {
              return const SizedBox.shrink();
            }
            
            return ValueListenableBuilder<String?>(
              valueListenable: ThemeController.filingType,
              builder: (context, filingType, _) {
                return Wrap(
                  spacing: spacing,
                  runSpacing: spacing,
                  children: _buildQuickActionCards(itemWidth, filingType),
                );
              },
            );
          },
        ),
      ],
    );
  }

  List<Widget> _buildQuickActionCards(double itemWidth, String? filingType) {
    List<Widget> cards = [];
    
    if (filingType == 'T1') {
      // T1 Personal user - show Your Forms instead of Business Tax, new filing goes to T1 directly
      cards.addAll([
        SizedBox(
          width: itemWidth,
          child: _buildActionCard(
            icon: Icons.add_circle_outline,
            title: 'New Filing',
            subtitle: 'Start T1 Personal',
            onTap: () => _handleT1NewFiling(),
          ),
        ),
        SizedBox(
          width: itemWidth,
          child: _buildActionCard(
            icon: Icons.folder_outlined,
            title: 'Your Forms',
            subtitle: 'View saved forms',
            onTap: () => context.go('/tax-forms/filled-forms'),
          ),
        ),
      ]);
    } else if (filingType == 'T2') {
      // T2 Business user - show Your Forms instead of Personal Tax, new filing goes to T2 directly  
      cards.addAll([
        SizedBox(
          width: itemWidth,
          child: _buildActionCard(
            icon: Icons.add_circle_outline,
            title: 'New Filing',
            subtitle: 'Start T2 Business',
            onTap: () => _handleT2NewFiling(),
          ),
        ),
        SizedBox(
          width: itemWidth,
          child: _buildActionCard(
            icon: Icons.folder_outlined,
            title: 'Your Forms',
            subtitle: 'View saved forms',
            onTap: () => context.go('/tax-forms/filled-forms'),
          ),
        ),
      ]);
    } else {
      // Default behavior (no filing type selected) - show both Personal and Business
      cards.addAll([
        SizedBox(
          width: itemWidth,
          child: _buildActionCard(
            icon: Icons.person_outline,
            title: 'Personal Tax',
            subtitle: 'File T1 return',
            onTap: () => _handlePersonalTaxTap(),
          ),
        ),
        SizedBox(
          width: itemWidth,
          child: _buildActionCard(
            icon: Icons.business_outlined,
            title: 'Business Tax',
            subtitle: 'File business return',
            onTap: () => _handleT2NewFiling(),
          ),
        ),
      ]);
    }
    
    // Always show Upload Documents and Track Status
    cards.addAll([
      SizedBox(
        width: itemWidth,
        child: _buildActionCard(
          icon: Icons.upload_file_outlined,
          title: 'Upload Documents',
          subtitle: 'Add tax documents',
          onTap: () => context.go('/documents'),
        ),
      ),
      SizedBox(
        width: itemWidth,
        child: _buildActionCard(
          icon: Icons.track_changes_outlined,
          title: 'Track Status',
          subtitle: 'Check filing status',
          onTap: () => context.go('/filing-status'),
        ),
      ),
    ]);
    
    return cards;
  }

  Widget _buildActionCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        constraints: const BoxConstraints(
          minHeight: 120,
          maxHeight: 140, // Prevent overflow
        ),
        padding: const EdgeInsets.all(AppDimensions.spacingSm),
        decoration: BoxDecoration(
          color: Theme.of(context).cardColor,
          borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
          border: Border.all(color: Theme.of(context).dividerColor),
          boxShadow: [
            BoxShadow(
              color: AppColors.shadowLight,
              blurRadius: 4,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(20),
              ),
              child: Icon(
                icon,
                color: AppColors.primary,
                size: 20,
              ),
            ),
            const SizedBox(height: 8),
            Flexible(
              child: Text(
                title,
                style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            const SizedBox(height: 2),
            Flexible(
              child: Text(
                subtitle,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                  color: AppColors.grey500,
                  fontSize: 11,
                ),
                textAlign: TextAlign.center,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentActivity() {
    final activities = [
      {
        'icon': Icons.check_circle_outline,
        'title': 'Personal Tax Return Filed',
        'subtitle': '2 days ago',
        'color': AppColors.success,
      },
      {
        'icon': Icons.upload_file_outlined,
        'title': 'Documents Uploaded',
        'subtitle': '1 week ago',
        'color': AppColors.primary,
      },
      {
        'icon': Icons.drafts_outlined,
        'title': 'Draft Saved',
        'subtitle': '2 weeks ago',
        'color': AppColors.warning,
      },
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Recent Activity',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        Container(
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            border: Border.all(color: Theme.of(context).dividerColor),
          ),
          child: ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: activities.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final activity = activities[index];
              return ListTile(
                leading: Icon(
                  activity['icon'] as IconData,
                  color: activity['color'] as Color,
                ),
                title: Text(
                  activity['title'] as String,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                subtitle: Text(activity['subtitle'] as String),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: AppDimensions.spacingMd,
                  vertical: AppDimensions.spacingSm,
                ),
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildTaxDeadlines() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Important Deadlines',
          style: Theme.of(context).textTheme.titleLarge?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
        const SizedBox(height: 16),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(AppDimensions.spacingMd),
          decoration: BoxDecoration(
            color: AppColors.warning.withValues(alpha: 0.1),
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            border: Border.all(color: AppColors.warning.withValues(alpha: 0.3)),
          ),
          child: Row(
            children: [
              Icon(
                Icons.schedule_outlined,
                color: AppColors.warning,
                size: 24,
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Tax Filing Deadline',
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.w600,
                        color: AppColors.grey800,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      'April 30, 2024 - 45 days remaining',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ],
    );
  }
}
