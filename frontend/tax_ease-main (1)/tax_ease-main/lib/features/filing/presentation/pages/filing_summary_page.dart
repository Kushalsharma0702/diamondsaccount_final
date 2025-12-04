import 'package:flutter/material.dart';

class FilingSummaryPage extends StatelessWidget {
  final String filingId;
  
  const FilingSummaryPage({
    super.key,
    required this.filingId,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Filing Summary')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.build, size: 64),
            const SizedBox(height: 16),
            Text('Filing ID: $filingId', style: const TextStyle(fontSize: 16)),
            const SizedBox(height: 8),
            const Text('Coming Soon', style: TextStyle(fontSize: 24)),
          ],
        ),
      ),
    );
  }
}
