import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';  // Make sure this import exists

class FilePickerWidget extends StatelessWidget {
  const FilePickerWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AppProvider>(
      builder: (context, provider, child) {
        return GestureDetector(
          onTap: provider.isLoading ? null : () {
            provider.pickFile();
          },
          child: Container(
            height: 150,
            decoration: BoxDecoration(
              color: Colors.purple[50],
              borderRadius: BorderRadius.circular(15),
              border: Border.all(
                color: provider.selectedFile != null 
                    ? Colors.green 
                    : Colors.purple[300]!,
                style: BorderStyle.solid,
                width: 2,
              ),
            ),
            child: Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    provider.selectedFile != null
                        ? Icons.check_circle
                        : Icons.cloud_upload,
                    size: 50,
                    color: provider.selectedFile != null
                        ? Colors.green
                        : Colors.purple,
                  ),
                  const SizedBox(height: 10),
                  Text(
                    provider.selectedFile != null
                        ? 'File Selected!'
                        : 'Tap to select audio file',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.w500,
                      color: provider.selectedFile != null
                          ? Colors.green[800]
                          : Colors.purple[800],
                    ),
                  ),
                  const SizedBox(height: 5),
                  if (provider.selectedFile != null)
                    Text(
                      provider.fileInfo,
                      style: const TextStyle(
                        fontSize: 12,
                        color: Colors.grey,
                      ),
                    )
                  else
                    Text(
                      'Supported: MP3, WAV, M4A, AAC, OGG, FLAC',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }
}