import 'package:flutter/material.dart';

class UploadDocumentsPage extends StatelessWidget {
  const UploadDocumentsPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Upload Documents')),
      body: const Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.build, size: 64),
            SizedBox(height: 16),
            Text('Coming Soon', style: TextStyle(fontSize: 24)),
          ],
        ),
      ),
    );
  }
}
