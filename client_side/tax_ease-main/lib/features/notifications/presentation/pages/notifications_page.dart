import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_text_styles.dart';

class NotificationsPage extends StatelessWidget {
  const NotificationsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Notifications'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () {
            if (Navigator.of(context).canPop()) {
              context.pop();
            } else {
              context.go('/home');
            }
          },
        ),
      ),
      body: const _NotificationsList(),
    );
  }
}

class _NotificationsList extends StatelessWidget {
  const _NotificationsList();

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final isSmall = constraints.maxWidth < 360;
        final titleStyle = (isSmall ? AppTextStyles.h3XSmall : AppTextStyles.h3Small)
            .copyWith(color: AppColors.grey800, fontWeight: FontWeight.w600);
        final subtitleStyle = (isSmall ? AppTextStyles.bodyXSmall : AppTextStyles.bodySmall)
            .copyWith(color: AppColors.grey600);

        return ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Header / tip
            Row(
              children: [
                const Icon(Icons.mark_chat_unread_outlined, size: 24, color: AppColors.grey600),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'Your latest communications and requests will appear here.',
                    style: subtitleStyle,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            // Demo notification (unread)
            _NotificationCard(
              title: 'Payment Request Sent',
              message: 'Please review and complete the payment to continue processing your return.',
              time: '2h ago',
              unread: true,
              titleStyle: titleStyle,
              subtitleStyle: subtitleStyle,
            ),
          ],
        );
      },
    );
  }
}

class _NotificationCard extends StatelessWidget {
  const _NotificationCard({
    required this.title,
    required this.message,
    required this.time,
    required this.unread,
    required this.titleStyle,
    required this.subtitleStyle,
  });

  final String title;
  final String message;
  final String time;
  final bool unread;
  final TextStyle titleStyle;
  final TextStyle subtitleStyle;

  @override
  Widget build(BuildContext context) {
    final Color borderColor = unread
        ? AppColors.brandPrimaryBlue
        : AppColors.brandLightBlue;
    final double borderWidth = unread ? 1.5 : 1.0;

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: borderColor.withValues(alpha: unread ? 0.7 : 0.4), width: borderWidth),
        boxShadow: const [
          BoxShadow(color: AppColors.shadowLight, blurRadius: 4, offset: Offset(0, 2)),
        ],
      ),
      child: ListTile(
        onTap: () => _openDialog(context),
        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        leading: Stack(
          alignment: Alignment.topRight,
          children: [
            Container(
              width: 36,
              height: 36,
              decoration: BoxDecoration(
                color: AppColors.primary.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: const Icon(Icons.attach_money, color: AppColors.primary),
            ),
            if (unread)
              Container(
                width: 10,
                height: 10,
                decoration: const BoxDecoration(
                  color: AppColors.error,
                  shape: BoxShape.circle,
                ),
              ),
          ],
        ),
        title: Text(
          title,
          style: titleStyle,
          softWrap: true,
        ),
        trailing: Text(time, style: subtitleStyle.copyWith(color: AppColors.grey500)),
      ),
    );
  }

  void _openDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Builder(
          builder: (context) {
            final w = MediaQuery.of(context).size.width;
            final isSmall = w < 360;
            final dialogTitleStyle = (isSmall ? AppTextStyles.h3XSmall : AppTextStyles.h3Small)
                .copyWith(fontWeight: FontWeight.w600);
            return Text(
              title,
              style: dialogTitleStyle,
              maxLines: 2,
              overflow: TextOverflow.ellipsis,
              softWrap: true,
            );
          },
        ),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                children: [
                  const Icon(Icons.access_time, size: 16, color: AppColors.grey600),
                  const SizedBox(width: 6),
                  Text(time, style: AppTextStyles.bodyXSmall.copyWith(color: AppColors.grey600)),
                ],
              ),
              const SizedBox(height: 12),
              Text(message, style: AppTextStyles.bodyMedium),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('Close'),
          ),
        ],
      ),
    );
  }
}
