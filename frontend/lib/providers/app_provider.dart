import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../services/api_service.dart';
import '../services/audio_service.dart';
import '../models/upload_response.dart';
import '../models/process_response.dart';

class AppProvider extends ChangeNotifier {
  final ApiService _apiService = ApiService();
  final AudioService _audioService = AudioService();

  // State variables
  PlatformFile? _selectedFile;
  UploadResponse? _uploadResponse;
  ProcessResponse? _processResponse;
  String? _selectedLanguage = 'auto';
  bool _isLoading = false;
  String _status = '';
  double _progress = 0.0;
  String? _lastDownloadUrl;
  Map<String, dynamic>? _lastTranslationFiles;
  Map<String, dynamic>? _diarizationResult;
  List<dynamic>? _generatedQuestions;
  Map<String, dynamic>? _chatResult;
  List<Map<String, dynamic>>? _actions;
  List<Map<String, dynamic>>? _topics;
  List<Map<String, dynamic>>? _flashcards;
  List<Map<String, dynamic>>? _mcqs;
  Map<String, dynamic>? _analytics;

  // Getters
  PlatformFile? get selectedFile => _selectedFile;
  UploadResponse? get uploadResponse => _uploadResponse;
  ProcessResponse? get processResponse => _processResponse;
  String? get selectedLanguage => _selectedLanguage;
  bool get isLoading => _isLoading;
  String get status => _status;
  double get progress => _progress;
  String? get lastDownloadUrl => _lastDownloadUrl;
  Map<String, dynamic>? get lastTranslationFiles => _lastTranslationFiles;
  Map<String, dynamic>? get diarizationResult => _diarizationResult;
  List<dynamic>? get generatedQuestions => _generatedQuestions;
  Map<String, dynamic>? get chatResult => _chatResult;
  List<Map<String, dynamic>>? get actions => _actions;
  List<Map<String, dynamic>>? get topics => _topics;
  List<Map<String, dynamic>>? get flashcards => _flashcards;
  List<Map<String, dynamic>>? get mcqs => _mcqs;
  Map<String, dynamic>? get analytics => _analytics;

  void selectLanguage(String? language) {
    _selectedLanguage = language;
    notifyListeners();
  }

  void setStatus(String status) {
    _status = status;
    notifyListeners();
  }

  Future<void> pickFile() async {
    try {
      _status = 'Selecting file...';
      notifyListeners();
      
      var file = await _audioService.pickAudioFile();
      if (file != null && _audioService.isSupportedFile(file)) {
        _selectedFile = file;
        _uploadResponse = null;
        _processResponse = null;
        _status = 'File selected: ${file.name}';
        notifyListeners();
      } else {
        _status = 'Please select a valid audio file';
        notifyListeners();
      }
    } catch (e) {
      _status = 'Error selecting file: $e';
      notifyListeners();
    }
  }

  Future<void> uploadAndProcess() async {
    if (_selectedFile == null) {
      _status = 'Please select a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _progress = 0.1;
      _status = 'Uploading file...';
      notifyListeners();

      _uploadResponse = await _apiService.uploadFile(_selectedFile!);
      _progress = 0.4;
      _status = 'File uploaded successfully! Processing...';
      notifyListeners();

      var language = _selectedLanguage ?? 'auto';
      _processResponse = await _apiService.processAudio(
        filePath: _uploadResponse!.path,
        language: language,
      );

      _progress = 1.0;
      if (_processResponse!.isSuccess) {
        _status = 'Processing complete! ✅';
      } else {
        _status = 'Error: ${_processResponse!.error ?? "Unknown error"} ❌';
      }
    } catch (e) {
      _status = 'Error: $e ❌';
      print('Upload/Process error: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> processOnlyTranscription() async {
    if (_selectedFile == null || _uploadResponse == null) {
      _status = 'Please upload a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = 'Transcribing...';
      notifyListeners();

      var language = _selectedLanguage ?? 'auto';
      _processResponse = await _apiService.transcribeOnly(
        filePath: _uploadResponse!.path,
        language: language,
      );

      if (_processResponse!.isSuccess) {
        _status = 'Transcription complete! ✅';
      } else {
        _status = 'Error: ${_processResponse!.error ?? "Unknown error"} ❌';
      }
    } catch (e) {
      _status = 'Error: $e ❌';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  // ==================== EXPORT METHODS ====================

  Future<void> exportPDF() async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '📄 Exporting PDF with timestamps...';
      notifyListeners();

      var result = await _apiService.exportPDF(
        _uploadResponse!.path,
        _selectedLanguage ?? 'auto',
        includeTimestamps: true,
      );

      _lastDownloadUrl = result['download_url'];
      _status = '✅ PDF exported! Download: ${result['download_url']}';
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _status = '❌ Export failed: $e';
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> exportCleanPDF() async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '📄 Exporting Clean PDF (no timestamps)...';
      notifyListeners();

      var result = await _apiService.exportClean(
        _uploadResponse!.path,
        _selectedLanguage ?? 'auto',
      );

      _lastDownloadUrl = result['download_url'];
      _status = '✅ Clean PDF exported! Download: ${result['download_url']}';
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _status = '❌ Export failed: $e';
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> exportDOCX() async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '📝 Exporting DOCX...';
      notifyListeners();

      var result = await _apiService.exportDOCX(
        _uploadResponse!.path,
        _selectedLanguage ?? 'auto',
      );

      _lastDownloadUrl = result['download_url'];
      _status = '✅ DOCX exported! Download: ${result['download_url']}';
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _status = '❌ Export failed: $e';
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> exportTranslated() async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '🌐 Translating to English...';
      notifyListeners();

      var result = await _apiService.exportTranslated(
        _uploadResponse!.path,
        _selectedLanguage ?? 'auto',
        targetLanguage: 'en',
      );

      _lastTranslationFiles = result['files'];
      _status = '✅ Translation exported!';
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _status = '❌ Translation failed: $e';
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> exportSummary() async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '📊 Exporting Summary...';
      notifyListeners();

      var result = await _apiService.exportSummary(
        _uploadResponse!.path,
        _selectedLanguage ?? 'auto',
      );

      _lastDownloadUrl = result['download_url'];
      _status = '✅ Summary exported! Download: ${result['download_url']}';
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      _status = '❌ Export failed: $e';
      _isLoading = false;
      notifyListeners();
    }
  }

  void reset() {
    _selectedFile = null;
    _uploadResponse = null;
    _processResponse = null;
    _isLoading = false;
    _status = '';
    _progress = 0.0;
    _lastDownloadUrl = null;
    _lastTranslationFiles = null;
    _diarizationResult = null;
    _generatedQuestions = null;
    _chatResult = null;
    _actions = null;
    _topics = null;
    _flashcards = null;
    _mcqs = null;
    _analytics = null;
    notifyListeners();
  }

  Future<void> checkHealth() async {
    try {
      var health = await _apiService.getHealth();
      _status = 'API Status: ${health['status']} ✅';
    } catch (e) {
      _status = 'API Status: Offline ❌';
    }
    notifyListeners();
  }

  // ==================== ADVANCED FEATURES ====================

  Future<void> runDiarization() async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '🎙️ Running speaker diarization...';
      notifyListeners();

      var transcriptPath = _processResponse?.savedTo ??
          _uploadResponse!.path.replaceAll(RegExp(r'\.\w+$'), '.txt');
      if (!transcriptPath.endsWith('.txt')) {
        transcriptPath = _uploadResponse!.path.replaceAll(RegExp(r'\.\w+$'), '.txt');
      }

      _diarizationResult = await _apiService.diarizeAudio(
        _uploadResponse!.path,
        transcriptPath,
      );

      _status = '✅ Diarization complete!';
    } catch (e) {
      _status = '❌ Diarization failed: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> runQuestionGeneration({int numQuestions = 5}) async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '❓ Generating questions...';
      notifyListeners();

      var transcriptPath = _processResponse?.savedTo ??
          _uploadResponse!.path.replaceAll(RegExp(r'\.\w+$'), '.txt');
      if (!transcriptPath.endsWith('.txt')) {
        transcriptPath = _uploadResponse!.path.replaceAll(RegExp(r'\.\w+$'), '.txt');
      }

      var result = await _apiService.generateQuestions(
        transcriptPath,
        numQuestions: numQuestions,
      );
      _generatedQuestions = result['questions'] != null
          ? List<dynamic>.from(result['questions'])
          : null;

      _status = '✅ Questions generated!';
    } catch (e) {
      _status = '❌ Question generation failed: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> runChat(String question) async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '💬 Chatting with transcript...';
      notifyListeners();

      _chatResult = await _apiService.chatWithTranscript(
        transcriptId: _uploadResponse!.fileId,
        question: question,
        filePath: _uploadResponse!.path,
      );

      _status = '✅ Chat response ready!';
    } catch (e) {
      _status = '❌ Chat failed: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> runActionExtraction() async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '📋 Extracting action items...';
      notifyListeners();

      var result = await _apiService.extractActions(_uploadResponse!.path);
      _actions = result['actions'] != null
          ? List<Map<String, dynamic>>.from(result['actions'])
          : null;

      _status = '✅ Action items extracted!';
    } catch (e) {
      _status = '❌ Action extraction failed: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> runTopicSegmentation() async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '📑 Segmenting topics...';
      notifyListeners();

      var result = await _apiService.segmentTopics(_uploadResponse!.path);
      _topics = result['topics'] != null
          ? List<Map<String, dynamic>>.from(result['topics'])
          : null;

      _status = '✅ Topics segmented!';
    } catch (e) {
      _status = '❌ Topic segmentation failed: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> runFlashcards({int numCards = 5}) async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '🃏 Generating flashcards...';
      notifyListeners();

      var result = await _apiService.generateFlashcards(
        _uploadResponse!.path,
        numCards: numCards,
      );
      _flashcards = result['flashcards'] != null
          ? List<Map<String, dynamic>>.from(result['flashcards'])
          : null;

      _status = '✅ Flashcards generated!';
    } catch (e) {
      _status = '❌ Flashcard generation failed: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> runMCQ({int numQuestions = 3}) async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '📝 Generating MCQs...';
      notifyListeners();

      var result = await _apiService.generateMCQ(
        _uploadResponse!.path,
        numQuestions: numQuestions,
      );
      _mcqs = result['mcqs'] != null
          ? List<Map<String, dynamic>>.from(result['mcqs'])
          : null;

      _status = '✅ MCQs generated!';
    } catch (e) {
      _status = '❌ MCQ generation failed: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> runAnalytics() async {
    if (_uploadResponse == null || _selectedFile == null) {
      _status = 'Please process a file first';
      notifyListeners();
      return;
    }

    try {
      _isLoading = true;
      _status = '📊 Computing analytics...';
      notifyListeners();

      _analytics = await _apiService.getAnalytics(
        filePath: _uploadResponse!.path,
      );

      _status = '✅ Analytics ready!';
    } catch (e) {
      _status = '❌ Analytics failed: $e';
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  String get fileInfo {
    if (_selectedFile == null) return 'No file selected';
    try {
      var size = _selectedFile!.size;
      if (size < 1024) {
        return '$size B';
      } else if (size < 1024 * 1024) {
        return '${(size / 1024).toStringAsFixed(1)} KB';
      } else if (size < 1024 * 1024 * 1024) {
        return '${(size / (1024 * 1024)).toStringAsFixed(1)} MB';
      } else {
        return '${(size / (1024 * 1024 * 1024)).toStringAsFixed(1)} GB';
      }
    } catch (e) {
      return 'File ready';
    }
  }
}