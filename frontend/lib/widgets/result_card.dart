// lib/widgets/result_card.dart
import 'package:flutter/material.dart';

class ResultCard extends StatelessWidget {
  final String title;
  final String? content;
  final IconData icon;
  final Color? color;
  final bool isTranscript;

  const ResultCard({
    super.key,
    required this.title,
    this.content,
    required this.icon,
    this.color,
    this.isTranscript = false,
  });

  @override
  Widget build(BuildContext context) {
    if (content == null || content!.isEmpty) return const SizedBox.shrink();

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(icon, color: color ?? Theme.of(context).colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  title,
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 12),
            isTranscript
                ? _buildTimestampedContent(content!)
                : Text(
                    content!,
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
          ],
        ),
      ),
    );
  }

  Widget _buildTimestampedContent(String content) {
    // Split into lines and build timestamped display
    final lines = content.split('\n');
    final List<Widget> widgets = [];
    
    for (var line in lines) {
      if (line.trim().isEmpty) continue;
      
      // Check if line starts with timestamp pattern [HH:MM:SS]
      final timestampRegex = RegExp(r'^\[\d{2}:\d{2}:\d{2}\.\d{3}\]');
      final match = timestampRegex.firstMatch(line);
      
      if (match != null) {
        final timestamp = match.group(0)!;
        final text = line.substring(timestamp.length).trim();
        
        widgets.add(
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.blue[100],
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    timestamp,
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                      color: Colors.blue,
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    text,
                    style: const TextStyle(fontSize: 14),
                  ),
                ),
              ],
            ),
          ),
        );
      } else {
        // Regular line without timestamp
        widgets.add(
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 2),
            child: Text(
              line,
              style: const TextStyle(fontSize: 14),
            ),
          ),
        );
      }
    }
    
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: widgets,
    );
  }
}

class QuestionsCard extends StatelessWidget {
  final List<dynamic>? questions;

  const QuestionsCard({super.key, this.questions});

  @override
  Widget build(BuildContext context) {
    if (questions == null || questions!.isEmpty) return const SizedBox.shrink();

    final displayQuestions = questions!.map((q) {
      if (q is String) return q;
      if (q is Map) return q['question']?.toString() ?? q.toString();
      return q.toString();
    }).toList();

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.quiz, color: Theme.of(context).colorScheme.primary),
                const SizedBox(width: 8),
                Text(
                  'Generated Questions (${displayQuestions.length})',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...displayQuestions.asMap().entries.map((entry) {
              final index = entry.key;
              final q = entry.value;
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: Text(
                  'Q${index + 1}. $q',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontWeight: FontWeight.w500,
                      ),
                ),
              );
            }),
          ],
        ),
      ),
    );
  }
}