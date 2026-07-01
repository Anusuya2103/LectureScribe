// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/app_provider.dart';
import '../widgets/file_picker_widget.dart';
import '../widgets/status_widget.dart';
import '../widgets/result_card.dart';
import '../utils/constants.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(AppConstants.appName),
        backgroundColor: Colors.purple,
        foregroundColor: Colors.white,
        elevation: 2,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () {
              context.read<AppProvider>().reset();
            },
          ),
          IconButton(
            icon: const Icon(Icons.health_and_safety),
            onPressed: () {
              context.read<AppProvider>().checkHealth();
            },
          ),
        ],
      ),
      body: Consumer<AppProvider>(
        builder: (context, provider, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const FilePickerWidget(),
                const SizedBox(height: 20),
                if (provider.selectedFile != null) ...[
                  _buildFileInfo(provider),
                  const SizedBox(height: 20),
                  _buildControls(provider),
                  const SizedBox(height: 20),
                ],
                const StatusWidget(),
                const SizedBox(height: 20),
                
                if (provider.uploadResponse != null && provider.selectedFile != null) ...[
                  _buildExportButtons(context, provider),
                ],
                
                if (provider.processResponse != null) ...[
                  const SizedBox(height: 20),
                  _buildResults(provider),
                  const SizedBox(height: 20),
                ],
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildFileInfo(AppProvider provider) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Colors.purple[50],
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.purple[200]!),
      ),
      child: Row(
        children: [
          const Icon(Icons.audio_file, color: Colors.purple, size: 30),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  provider.selectedFile!.name,
                  style: const TextStyle(fontWeight: FontWeight.bold),
                  overflow: TextOverflow.ellipsis,
                ),
                Text(
                  'Size: ${provider.fileInfo}',
                  style: TextStyle(color: Colors.grey[600], fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildControls(AppProvider provider) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        children: [
          DropdownButtonFormField<String>(
            initialValue: provider.selectedLanguage ?? 'auto',
            decoration: const InputDecoration(
              labelText: 'Language',
              border: OutlineInputBorder(),
              filled: true,
              fillColor: Colors.white,
            ),
            items: AppConstants.languages.entries.map((entry) {
              return DropdownMenuItem(
                value: entry.key,
                child: Text(entry.value),
              );
            }).toList(),
            onChanged: (value) {
              provider.selectLanguage(value);
            },
          ),
          const SizedBox(height: 10),
          Row(
            children: [
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: provider.isLoading ? null : () {
                    provider.uploadAndProcess();
                  },
                  icon: provider.isLoading
                      ? const SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: Colors.white,
                          ),
                        )
                      : const Icon(Icons.play_arrow),
                  label: Text(
                    provider.isLoading ? 'Processing...' : 'Full Process',
                  ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.green,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 15),
                  ),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: provider.isLoading ? null : () {
                    provider.processOnlyTranscription();
                  },
                  icon: const Icon(Icons.mic),
                  label: const Text('Transcribe Only'),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue,
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(vertical: 15),
                  ),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildResults(AppProvider provider) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (provider.processResponse!.segments != null && provider.processResponse!.segments!.isNotEmpty)
          _buildTimestampedTranscript(provider.processResponse!.segments!)
        else if (provider.processResponse!.transcript != null && provider.processResponse!.transcript!.isNotEmpty)
          ResultCard(
            title: '📝 Transcript',
            content: provider.processResponse!.transcript,
            icon: Icons.text_snippet,
            color: Colors.blue,
          ),

        const SizedBox(height: 20),

        _buildTabbedResults(provider),
      ],
    );
  }

  Widget _buildTimestampedTranscript(List<Map<String, dynamic>> segments) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.timer, color: Colors.blue),
              const SizedBox(width: 8),
              Text(
                '📝 Transcript',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          ...segments.map((seg) {
            final start = seg['start'] ?? 0;
            final end = seg['end'] ?? 0;
            final text = seg['text'] ?? '';
            return Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.blue.withValues(alpha: 0.2),
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: Text(
                      '${_formatTime(start)} -> ${_formatTime(end)}',
                      style: const TextStyle(fontSize: 11, color: Colors.blueGrey),
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
            );
          }),
        ],
      ),
    );
  }

  String _formatTime(double seconds) {
    final mins = seconds ~/ 60;
    final secs = (seconds % 60).toInt();
    return '${mins.toString().padLeft(2, '0')}:${secs.toString().padLeft(2, '0')}';
  }

  Widget _buildTabbedResults(AppProvider provider) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.grey[50],
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.grey[300]!),
      ),
      child: Column(
        children: [
          TabBar(
            controller: _tabController,
            tabs: const [
              Tab(text: 'Summary'),
              Tab(text: 'Questions'),
              Tab(text: 'Advanced'),
            ],
            labelColor: Colors.purple,
            unselectedLabelColor: Colors.grey,
            indicatorColor: Colors.purple,
          ),
          SizedBox(
            height: 400,
            child: TabBarView(
              controller: _tabController,
              children: [
                _buildSummaryTab(provider),
                _buildQuestionsTab(provider),
                _buildAdvancedTab(provider),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSummaryTab(AppProvider provider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          ResultCard(
            title: '📄 Summary',
            content: provider.processResponse!.summary ?? 'No summary available',
            icon: Icons.summarize,
            color: Colors.green,
          ),
        ],
      ),
    );
  }

  Widget _buildQuestionsTab(AppProvider provider) {
    final questions = <String>[];
    if (provider.processResponse!.questions != null) {
      questions.addAll(provider.processResponse!.questions!);
    }
    if (provider.generatedQuestions != null) {
      questions.addAll(provider.generatedQuestions!.cast<String>());
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: questions.isEmpty
          ? const Center(child: Text('No questions generated yet'))
          : QuestionsCard(questions: questions),
    );
  }

  Widget _buildAdvancedTab(AppProvider provider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            '✨ Advanced Features',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildAdvancedButton(
                icon: Icons.mic,
                label: 'Diarize',
                color: Colors.teal,
                onPressed: provider.isLoading ? null : () => provider.runDiarization(),
              ),
              _buildAdvancedButton(
                icon: Icons.quiz,
                label: 'Questions',
                color: Colors.indigo,
                onPressed: provider.isLoading ? null : () => provider.runQuestionGeneration(),
              ),
              _buildAdvancedButton(
                icon: Icons.chat,
                label: 'Chat',
                color: Colors.deepOrange,
                onPressed: provider.isLoading ? null : () => provider.runChat('Summarize this lecture'),
              ),
              _buildAdvancedButton(
                icon: Icons.assignment,
                label: 'Actions',
                color: Colors.brown,
                onPressed: provider.isLoading ? null : () => provider.runActionExtraction(),
              ),
              _buildAdvancedButton(
                icon: Icons.topic,
                label: 'Topics',
                color: Colors.blueGrey,
                onPressed: provider.isLoading ? null : () => provider.runTopicSegmentation(),
              ),
              _buildAdvancedButton(
                icon: Icons.style,
                label: 'Flashcards',
                color: Colors.pink,
                onPressed: provider.isLoading ? null : () => provider.runFlashcards(),
              ),
              _buildAdvancedButton(
                icon: Icons.check_circle,
                label: 'MCQs',
                color: Colors.lime,
                onPressed: provider.isLoading ? null : () => provider.runMCQ(),
              ),
              _buildAdvancedButton(
                icon: Icons.analytics,
                label: 'Analytics',
                color: Colors.cyan,
                onPressed: provider.isLoading ? null : () => provider.runAnalytics(),
              ),
            ],
          ),
          const SizedBox(height: 20),
          _buildAdvancedResults(provider),
        ],
      ),
    );
  }

  Widget _buildAdvancedButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback? onPressed,
  }) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 16),
      label: Text(label),
      style: ElevatedButton.styleFrom(
        backgroundColor: color.withValues(alpha: 0.1),
        foregroundColor: color,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        minimumSize: const Size(80, 36),
        disabledBackgroundColor: Colors.grey[300],
        disabledForegroundColor: Colors.grey[600],
      ),
    );
  }

  Widget _buildAdvancedResults(AppProvider provider) {
    final List<Widget> results = [];

    if (provider.diarizationResult != null && provider.diarizationResult!['labeled_transcript'] != null) {
      results.add(
        ResultCard(
          title: '🎙️ Diarization Result',
          content: provider.diarizationResult!['labeled_transcript'],
          icon: Icons.groups,
          color: Colors.teal,
        ),
      );
    }

    if (provider.chatResult != null) {
      results.add(
        ResultCard(
          title: '💬 Chat Response',
          content: provider.chatResult!['answer'] ?? 'No response',
          icon: Icons.chat,
          color: Colors.deepOrange,
        ),
      );
    }

    if (provider.actions != null && provider.actions!.isNotEmpty) {
      final actionsText = (provider.actions as List).map((a) => a['description'] ?? a.toString()).join('\n');
      results.add(
        ResultCard(
          title: '📋 Action Items',
          content: actionsText,
          icon: Icons.assignment,
          color: Colors.brown,
        ),
      );
    }

    if (provider.topics != null && provider.topics!.isNotEmpty) {
      final topicsText = (provider.topics as List).map((t) => t['topic'] ?? t.toString()).join('\n');
      results.add(
        ResultCard(
          title: '📑 Topics',
          content: topicsText,
          icon: Icons.topic,
          color: Colors.blueGrey,
        ),
      );
    }

    if (provider.flashcards != null && provider.flashcards!.isNotEmpty) {
      final flashcardsText = (provider.flashcards as List).map((f) {
        final q = f['question'] ?? '';
        final a = f['answer'] ?? '';
        return 'Q: $q\nA: $a';
      }).join('\n\n');
      results.add(
        ResultCard(
          title: '🃏 Flashcards',
          content: flashcardsText,
          icon: Icons.style,
          color: Colors.pink,
        ),
      );
    }

    if (provider.mcqs != null && provider.mcqs!.isNotEmpty) {
      final mcqsText = (provider.mcqs as List).map((m) {
        final q = m['question'] ?? '';
        final opts = m['options'] ?? [];
        return 'Q: $q\nOptions: ${opts.join(", ")}';
      }).join('\n\n');
      results.add(
        ResultCard(
          title: '📝 MCQs',
          content: mcqsText,
          icon: Icons.check_circle,
          color: Colors.lime,
        ),
      );
    }

    if (provider.analytics != null) {
      results.add(
        ResultCard(
          title: '📊 Analytics',
          content: _formatAnalytics(provider.analytics!),
          icon: Icons.analytics,
          color: Colors.cyan,
        ),
      );
    }

    if (results.isEmpty) {
      return const SizedBox.shrink();
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: results,
    );
  }

  String _formatAnalytics(Map<String, dynamic> analytics) {
    final buffer = StringBuffer();
    if (analytics['summary'] != null) {
      final s = analytics['summary'];
      buffer.writeln('Words: ${s['total_words'] ?? 0}');
      buffer.writeln('Sentences: ${s['total_sentences'] ?? 0}');
      buffer.writeln('Unique Words: ${s['unique_words'] ?? 0}');
    }
    if (analytics['readability'] != null) {
      final r = analytics['readability'];
      buffer.writeln('Readability: ${r['flesch_score'] ?? 'N/A'}');
    }
    if (analytics['top_keywords'] != null) {
      final keywords = analytics['top_keywords'] as List;
      buffer.writeln('Keywords: ${keywords.join(", ")}');
    }
    if (analytics['sentiment'] != null) {
      buffer.writeln('Sentiment: ${analytics['sentiment']}');
    }
    return buffer.toString();
  }

  Widget _buildExportButtons(BuildContext context, AppProvider provider) {
    return Container(
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Icon(Icons.upload_file, color: Colors.blue),
              const SizedBox(width: 8),
              Text(
                '📤 Export Options',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 16,
                ),
              ),
            ],
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _buildExportButton(
                icon: Icons.picture_as_pdf,
                label: 'PDF',
                color: Colors.red,
                onPressed: provider.isLoading ? null : () => provider.exportPDF(),
              ),
              _buildExportButton(
                icon: Icons.cleaning_services,
                label: 'Clean PDF',
                color: Colors.orange,
                onPressed: provider.isLoading ? null : () => provider.exportCleanPDF(),
              ),
              _buildExportButton(
                icon: Icons.description,
                label: 'DOCX',
                color: Colors.blue,
                onPressed: provider.isLoading ? null : () => provider.exportDOCX(),
              ),
              _buildExportButton(
                icon: Icons.translate,
                label: 'Translate',
                color: Colors.green,
                onPressed: provider.isLoading ? null : () => provider.exportTranslated(),
              ),
              _buildExportButton(
                icon: Icons.summarize,
                label: 'Summary',
                color: Colors.purple,
                onPressed: provider.isLoading ? null : () => provider.exportSummary(),
              ),
            ],
          ),
          if (provider.lastDownloadUrl != null) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green[200]!),
              ),
              child: Row(
                children: [
                  const Icon(Icons.download, color: Colors.green),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      'Download: ${provider.lastDownloadUrl!.split('/').last}',
                      style: const TextStyle(fontSize: 12),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.copy, size: 16),
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('Link copied to clipboard!')),
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
          if (provider.lastTranslationFiles != null) ...[
            const SizedBox(height: 10),
            Container(
              padding: const EdgeInsets.all(10),
              decoration: BoxDecoration(
                color: Colors.green[50],
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.green[200]!),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '📄 Translation Files:',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 5),
                  if (provider.lastTranslationFiles!['docx'] != null)
                    Text('DOCX: ${provider.lastTranslationFiles!['docx']}'),
                  if (provider.lastTranslationFiles!['txt'] != null)
                    Text('TXT: ${provider.lastTranslationFiles!['txt']}'),
                ],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildExportButton({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback? onPressed,
  }) {
    return ElevatedButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 16),
      label: Text(label),
      style: ElevatedButton.styleFrom(
        backgroundColor: color.withValues(alpha: 0.1),
        foregroundColor: color,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        minimumSize: const Size(80, 36),
        disabledBackgroundColor: Colors.grey[300],
        disabledForegroundColor: Colors.grey[600],
      ),
    );
  }
}