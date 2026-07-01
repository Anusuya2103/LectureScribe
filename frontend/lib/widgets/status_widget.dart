import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';

class StatusWidget extends StatelessWidget {
  const StatusWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return Consumer<AppProvider>(
      builder: (context, provider, child) {
        if (provider.status.isEmpty) return const SizedBox.shrink();

        Color backgroundColor;
        Color textColor;
        IconData icon;

        if (provider.status.contains('✅')) {
          backgroundColor = Colors.green[100]!;
          textColor = Colors.green[900]!;
          icon = Icons.check_circle;
        } else if (provider.status.contains('❌')) {
          backgroundColor = Colors.red[100]!;
          textColor = Colors.red[900]!;
          icon = Icons.error;
        } else if (provider.status.contains('...')) {
          backgroundColor = Colors.blue[100]!;
          textColor = Colors.blue[900]!;
          icon = Icons.hourglass_top;
        } else {
          backgroundColor = Colors.grey[200]!;
          textColor = Colors.grey[800]!;
          icon = Icons.info;
        }

        return Container(
          padding: const EdgeInsets.all(15),
          decoration: BoxDecoration(
            color: backgroundColor,
            borderRadius: BorderRadius.circular(10),
          ),
          child: Row(
            children: [
              Icon(icon, color: textColor),
              const SizedBox(width: 10),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      provider.status,
                      style: TextStyle(
                        color: textColor,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    if (provider.isLoading) const SizedBox(height: 8),
                    if (provider.isLoading)
                      LinearProgressIndicator(
                        value: provider.progress,
                        backgroundColor: Colors.grey[300],
                        valueColor: const AlwaysStoppedAnimation<Color>(
                          Colors.purple,
                        ),
                      ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}