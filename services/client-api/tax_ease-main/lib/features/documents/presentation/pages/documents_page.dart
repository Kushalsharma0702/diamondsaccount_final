import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../../../../core/constants/app_colors.dart';
import '../../../../core/constants/app_dimensions.dart';
import '../../../../core/utils/smooth_scroll_physics.dart';
import '../../../../core/utils/responsive.dart';
import '../../../../shared/animations/smooth_animations.dart';
import '../../data/files_api.dart';

class DocumentsPage extends StatefulWidget {
  const DocumentsPage({super.key});

  @override
  State<DocumentsPage> createState() => _DocumentsPageState();
}

class _DocumentsPageState extends State<DocumentsPage> {
  final List<String> _uploadedFileNames = [];
  bool _isUploading = false;

  Future<void> _pickAndUpload() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowMultiple: false,
        allowedExtensions: const ['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx'],
        withReadStream: false,
        withData: false,
      );
      if (result == null || result.files.isEmpty) return; // user canceled

      final file = result.files.single;
      final path = file.path;
      if (path == null) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Could not access the selected file path.')),
          );
        }
        return;
      }

      setState(() => _isUploading = true);
      final resp = await FilesApi.uploadFile(filePath: path);

      // Prefer original filename from API if provided, else from picker
      final name = (resp['original_filename'] ?? file.name)?.toString() ?? 'Uploaded file';

      if (mounted) {
        setState(() {
          _uploadedFileNames.add(name);
          _isUploading = false;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Uploaded: $name')),
        );
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isUploading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Upload failed: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Documents'),
        automaticallyImplyLeading: false,
        actions: [
          IconButton(
            icon: const Icon(Icons.upload_outlined),
            onPressed: _isUploading ? null : _pickAndUpload,
            tooltip: 'Upload document',
          ),
        ],
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
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              SmoothAnimations.slideUp(
                child: Text(
                  'Your Documents',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ),
              const SizedBox(height: 24),
              if (_isUploading)
                const LinearProgressIndicator(minHeight: 2),
              const SizedBox(height: 12),
              SmoothAnimations.slideUp(
                delay: const Duration(milliseconds: 200),
                child: _buildDocumentsList(),
              ),
            ],
          ),
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _isUploading ? null : _pickAndUpload,
        child: const Icon(Icons.add),
      ),
    );
  }

  Widget _buildDocumentsList() {
    return Builder(
      builder: (context) {
        if (_uploadedFileNames.isEmpty) {
          return Container(
            width: double.infinity,
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              color: Theme.of(context).cardColor,
              borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
              border: Border.all(color: Theme.of(context).dividerColor),
            ),
            child: const Center(
              child: Text('No documents uploaded yet.'),
            ),
          );
        }

        return Container(
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            borderRadius: BorderRadius.circular(AppDimensions.radiusLg),
            border: Border.all(color: Theme.of(context).dividerColor),
          ),
          child: ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: _uploadedFileNames.length,
            separatorBuilder: (context, index) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final name = _uploadedFileNames[index];
              return ListTile(
                leading: const Icon(
                  Icons.description,
                  color: AppColors.primary,
                ),
                title: Text(
                  name,
                  style: const TextStyle(fontWeight: FontWeight.w500),
                ),
                trailing: IconButton(
                  icon: const Icon(Icons.more_vert),
                  onPressed: () {},
                ),
              );
            },
          ),
        );
      },
    );
  }
}
