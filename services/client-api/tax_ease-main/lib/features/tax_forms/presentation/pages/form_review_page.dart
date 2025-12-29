import 'package:flutter/material.dart';

class FormReviewPage extends StatelessWidget {
  final String formType;
  
  const FormReviewPage({
    super.key,
    required this.formType,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Review ${formType.toUpperCase()} Form')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.build, size: 64),
            const SizedBox(height: 16),
            Text('$formType Tax Form Review', style: const TextStyle(fontSize: 20)),
            const SizedBox(height: 8),
            const Text('Coming Soon', style: TextStyle(fontSize: 24)),
          ],
        ),
      ),
    );
  }
}
