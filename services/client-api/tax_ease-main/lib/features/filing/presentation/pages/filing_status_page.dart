import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:go_router/go_router.dart';
import '../../../tax_forms/data/services/t1_form_storage_service.dart';
import '../../../tax_forms/data/services/t2_form_storage_service.dart';
import '../../../tax_forms/data/services/unified_form_service.dart';
import '../../../../../core/constants/app_colors.dart';
import '../../../../../core/constants/app_text_styles.dart';

class FilingStatusPage extends StatefulWidget {
  const FilingStatusPage({super.key});

  @override
  State<FilingStatusPage> createState() => _FilingStatusPageState();
}

class _FilingStatusPageState extends State<FilingStatusPage> {
  late Future<_FilingStatusInfo?> _future;

  static const List<String> _steps = [
    'Form in Draft',
    'Form Submitted',
    'Payment Request Sent',
    'Payment Received',
    'Return in Progress',
    'Additional Information Required',
    'Under Review / Pending Approval',
    'Approved for Filing',
    'E-Filing Completed – Acknowledgment and Documents Available for Download',
  ];

  @override
  void initState() {
    super.initState();
    _future = _loadMostRecentStatus();
  }

  Future<_FilingStatusInfo?> _loadMostRecentStatus() async {
    final t1 = await T1FormStorageService.instance.loadAllForms();
    final t2 = await T2FormStorageService.instance.loadAllForms();

    final List<CombinedFormProgress> all = [];

    for (final f in t1) {
      all.add(
        CombinedFormProgress(
          formId: f.id,
          formType: 'T1',
          status: f.status,
          updatedAt: f.updatedAt,
          progress: T1FormStorageService.instance.calculateFormProgress(f),
          t1Form: f,
          t2Form: null,
        ),
      );
    }
    for (final f in t2) {
      all.add(
        CombinedFormProgress(
          formId: f.id,
          formType: 'T2',
          status: f.status,
          updatedAt: f.updatedAt,
          progress: T2FormStorageService.instance.calculateFormProgress(f),
          t1Form: null,
          t2Form: f,
        ),
      );
    }

    if (all.isEmpty) return null;

    all.sort((a, b) => (b.updatedAt ?? DateTime(0)).compareTo(a.updatedAt ?? DateTime(0)));
    final mostRecent = all.first;

    // Map existing simple statuses to 9-step pipeline
    final int stepIndex = _mapStatusToStepIndex(mostRecent);

    return _FilingStatusInfo(
      formId: mostRecent.formId,
      formType: mostRecent.formType,
      updatedAt: mostRecent.updatedAt,
      currentStepIndex: stepIndex,
      steps: _steps,
    );
  }

  int _mapStatusToStepIndex(CombinedFormProgress form) {
    // Minimal mapping with today\'s available data; can be enhanced later when backend adds more states.
    // draft -> step 0
    if (form.status.toLowerCase() == 'draft') return 0;
    // submitted -> treat as under review for now (closest to our flow)
    if (form.status.toLowerCase() == 'submitted') return 6; // Under Review / Pending Approval

    // fallback
    return 0;
  }

  void _refresh() {
    setState(() {
      _future = _loadMostRecentStatus();
    });
  }

  @override
  Widget build(BuildContext context) {

    return Scaffold(
      appBar: AppBar(
        title: const Text('Filing Status'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (Navigator.of(context).canPop()) {
              Navigator.of(context).pop();
            } else {
              context.go('/home');
            }
          },
        ),
        actions: [
          IconButton(
            tooltip: 'Refresh',
            onPressed: _refresh,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: FutureBuilder<_FilingStatusInfo?>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return _ErrorState(onRetry: _refresh);
          }
          final info = snapshot.data;
          if (info == null) {
            return _EmptyState(onStart: () => _goToForms(context));
          }

          return CustomScrollView(
            slivers: [
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: _HeaderCard(info: info),
                ),
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
                  child: _Timeline(steps: info.steps, currentIndex: info.currentStepIndex),
                ),
              ),
              SliverToBoxAdapter(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: LayoutBuilder(
                    builder: (context, constraints) {
                      final isNarrow = constraints.maxWidth < 380;
                      final actions = [
OutlinedButton(
                          onPressed: () => context.push('/notifications'),
                          child: const Text('Communication'),
                        ),
                        ElevatedButton(
                          onPressed: () => _goToForms(context),
                          child: const Text('View Forms'),
                        ),
                      ];

                      if (isNarrow) {
                        return Column(
                          crossAxisAlignment: CrossAxisAlignment.stretch,
                          children: [
                            actions[0],
                            const SizedBox(height: 12),
                            actions[1],
                          ],
                        );
                      }
                      return Row(
                        children: [
                          Expanded(child: actions[0]),
                          const SizedBox(width: 12),
                          Expanded(child: actions[1]),
                        ],
                      );
                    },
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }

  void _goToForms(BuildContext context) {
    // Use the provided helper to jump to forms hub
    final route = UnifiedFormService.instance.getMostRecentFormRoute();
    context.go(route);
  }
}

class _HeaderCard extends StatelessWidget {
  const _HeaderCard({required this.info});
  final _FilingStatusInfo info;

  @override
  Widget build(BuildContext context) {
    final dateText = info.updatedAt != null
        ? DateFormat('MMM d, yyyy • h:mm a').format(info.updatedAt!.toLocal())
        : 'Unknown';

    return Container(
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(16),
        gradient: const LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppColors.brandLightBlue,
            AppColors.brandPrimaryBlue,
          ],
        ),
        boxShadow: const [
          BoxShadow(color: AppColors.shadowMedium, blurRadius: 12, offset: Offset(0, 8)),
        ],
      ),
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.assignment_turned_in_rounded, color: Colors.white),
              const SizedBox(width: 8),
              Text(
                'Most Recent Form',
style: AppTextStyles.bodySmall.copyWith(color: Colors.white.withValues(alpha: 0.9)),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            '${info.formType} Return',
            style: AppTextStyles.h2LargeWhite,
          ),
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
_Chip(text: info.steps[info.currentStepIndex], color: Colors.white.withValues(alpha: 0.15)),
_Chip(icon: Icons.schedule_rounded, text: 'Updated $dateText', color: Colors.white.withValues(alpha: 0.15)),
            ],
          ),
        ],
      ),
    );
  }

}

class _Chip extends StatelessWidget {
  const _Chip({required this.text, this.icon, this.color});
  final String text;
  final IconData? icon;
  final Color? color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color ?? AppColors.containerLight,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: Colors.white24, width: 1),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 14, color: Colors.white),
            const SizedBox(width: 6),
          ],
          Text(
            text,
            style: AppTextStyles.bodyXSmall.copyWith(color: Colors.white),
          ),
        ],
      ),
    );
  }
}

class _Timeline extends StatelessWidget {
  const _Timeline({required this.steps, required this.currentIndex});
  final List<String> steps;
  final int currentIndex;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.zero,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            for (int i = 0; i < steps.length; i++) _TimelineTile(
              title: steps[i],
              index: i,
              isDone: i < currentIndex,
              isCurrent: i == currentIndex,
              isLast: i == steps.length - 1,
            ),
          ],
        ),
      ),
    );
  }
}

class _TimelineTile extends StatelessWidget {
  const _TimelineTile({
    required this.title,
    required this.index,
    required this.isDone,
    required this.isCurrent,
    required this.isLast,
  });

  final String title;
  final int index;
  final bool isDone;
  final bool isCurrent;
  final bool isLast;

  Color get _dotColor => isDone || isCurrent ? AppColors.brandPrimaryBlue : AppColors.grey400;
  Color get _titleColor => isDone || isCurrent ? AppColors.grey900 : AppColors.grey600;

  @override
  Widget build(BuildContext context) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Column(
          children: [
            _Dot(state: isDone ? _DotState.done : (isCurrent ? _DotState.current : _DotState.pending), color: _dotColor, index: index),
            if (!isLast) _Connector(color: isDone ? AppColors.brandPrimaryBlue : AppColors.grey300),
          ],
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Padding(
            padding: EdgeInsets.only(top: isCurrent ? 2 : 4, bottom: isLast ? 0 : 16),
            child: Text(
              title,
              style: (isCurrent ? AppTextStyles.bodyLarge : AppTextStyles.bodyMedium).copyWith(
                color: _titleColor,
                fontWeight: isCurrent ? FontWeight.w600 : FontWeight.w400,
              ),
            ),
          ),
        ),
      ],
    );
  }
}

enum _DotState { done, current, pending }

class _Dot extends StatelessWidget {
  const _Dot({required this.state, required this.color, required this.index});
  final _DotState state;
  final Color color;
  final int index;

  @override
  Widget build(BuildContext context) {
    switch (state) {
      case _DotState.done:
        return Container(
          width: 20,
          height: 20,
          decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          child: const Icon(Icons.check, size: 14, color: Colors.white),
        );
      case _DotState.current:
        return Container(
          width: 20,
          height: 20,
          decoration: BoxDecoration(shape: BoxShape.circle, border: Border.all(color: color, width: 2)),
          alignment: Alignment.center,
          child: Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
        );
      case _DotState.pending:
        return Container(
          width: 20,
          height: 20,
          decoration: BoxDecoration(shape: BoxShape.circle, border: Border.all(color: AppColors.grey400, width: 2)),
        );
    }
  }
}

class _Connector extends StatelessWidget {
  const _Connector({required this.color});
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 2,
      height: 28,
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(2),
      ),
      margin: const EdgeInsets.symmetric(vertical: 6),
    );
  }
}

class _EmptyState extends StatelessWidget {
  const _EmptyState({required this.onStart});
  final VoidCallback onStart;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.inbox_outlined, size: 64, color: AppColors.grey500),
            const SizedBox(height: 12),
            Text('No forms yet', style: AppTextStyles.h3Medium.copyWith(color: AppColors.grey800)),
            const SizedBox(height: 6),
            Text('Start a new form to see your filing status here.', style: AppTextStyles.bodySmall.copyWith(color: AppColors.grey600)),
            const SizedBox(height: 16),
            ElevatedButton(onPressed: onStart, child: const Text('Start a Form')),
          ],
        ),
      ),
    );
  }
}

class _ErrorState extends StatelessWidget {
  const _ErrorState({required this.onRetry});
  final VoidCallback onRetry;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.error_outline, size: 64, color: AppColors.error),
            const SizedBox(height: 12),
            Text('Something went wrong', style: AppTextStyles.h3Medium.copyWith(color: AppColors.grey800)),
            const SizedBox(height: 6),
            Text('Please try again in a moment.', style: AppTextStyles.bodySmall.copyWith(color: AppColors.grey600)),
            const SizedBox(height: 16),
            OutlinedButton(onPressed: onRetry, child: const Text('Retry')),
          ],
        ),
      ),
    );
  }
}

class _FilingStatusInfo {
  const _FilingStatusInfo({
    required this.formId,
    required this.formType,
    required this.updatedAt,
    required this.currentStepIndex,
    required this.steps,
  });
  final String formId;
  final String formType; // T1 or T2
  final DateTime? updatedAt;
  final int currentStepIndex; // 0..8
  final List<String> steps;
}
