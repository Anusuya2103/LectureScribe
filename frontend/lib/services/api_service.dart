import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:file_picker/file_picker.dart';
import '../models/upload_response.dart';
import '../models/process_response.dart';
import '../utils/constants.dart';

class ApiService {
  final String baseUrl = AppConstants.apiBaseUrl;

  // ==================== UPLOAD ====================
  Future<UploadResponse> uploadFile(PlatformFile file) async {
    try {
      print('Uploading file: ${file.name}');
      
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/api/upload'),
      );
      
      if (file.bytes != null && file.bytes!.isNotEmpty) {
        request.files.add(
          http.MultipartFile.fromBytes(
            'file',
            file.bytes!,
            filename: file.name,
          ),
        );
      } else if (file.path != null) {
        request.files.add(
          await http.MultipartFile.fromPath(
            'file',
            file.path!,
          ),
        );
      } else {
        throw Exception('No file data available');
      }

      print('Sending request...');
      var streamedResponse = await request.send();
      var response = await http.Response.fromStream(streamedResponse);
      
      print('Response status: ${response.statusCode}');
      print('Response body: ${response.body}');

      if (response.statusCode != 200) {
        throw Exception('Upload failed: ${response.statusCode} - ${response.body}');
      }

      var data = json.decode(response.body);
      return UploadResponse.fromJson(data);
    } catch (e) {
      print('Upload error: $e');
      throw Exception('Upload error: $e');
    }
  }

  // ==================== PROCESS ====================
  Future<ProcessResponse> processAudio({
    required String filePath,
    String language = 'auto',
  }) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/process'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
          'language': language,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Processing failed: ${response.statusCode}');
      }

      var data = json.decode(response.body);
      return ProcessResponse.fromJson(data);
    } catch (e) {
      throw Exception('Processing error: $e');
    }
  }

  Future<ProcessResponse> transcribeOnly({
    required String filePath,
    String language = 'auto',
  }) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/transcribe'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
          'language': language,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Transcription failed: ${response.statusCode}');
      }

      var data = json.decode(response.body);
      return ProcessResponse.fromJson(data);
    } catch (e) {
      throw Exception('Transcription error: $e');
    }
  }

  // ==================== HEALTH ====================
  Future<Map<String, dynamic>> getHealth() async {
    try {
      var response = await http.get(
        Uri.parse('$baseUrl/health'),
      );

      if (response.statusCode != 200) {
        throw Exception('Health check failed');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Health check error: $e');
    }
  }

  // ==================== DIARIZATION ====================

  Future<Map<String, dynamic>> diarizeAudio(
    String audioPath,
    String transcriptPath,
  ) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/diarize'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'audio_path': audioPath,
          'transcript_path': transcriptPath,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Diarization failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Diarization error: $e');
    }
  }

  // ==================== QUESTIONS ====================

  Future<Map<String, dynamic>> generateQuestions(
    String transcriptPath, {
    int numQuestions = 5,
  }) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/questions'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'transcript_path': transcriptPath,
          'num_questions': numQuestions,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Question generation failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Question generation error: $e');
    }
  }

  // ==================== CHAT ====================

  Future<Map<String, dynamic>> chatWithTranscript({
    required String transcriptId,
    required String question,
    String? filePath,
  }) async {
    try {
      final queryParams = {
        'transcript_id': transcriptId,
        'question': question,
        if (filePath != null) 'file_path': filePath,
      };
      var response = await http.post(
        Uri.parse('$baseUrl/api/chat').replace(queryParameters: queryParams),
        headers: {'Content-Type': 'application/json'},
      );

      if (response.statusCode != 200) {
        throw Exception('Chat failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Chat error: $e');
    }
  }

  // ==================== ACTIONS ====================

  Future<Map<String, dynamic>> extractActions(String filePath) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/actions'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Action extraction failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Action extraction error: $e');
    }
  }

  // ==================== TOPICS ====================

  Future<Map<String, dynamic>> segmentTopics(String filePath) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/topics'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Topic segmentation failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Topic segmentation error: $e');
    }
  }

  // ==================== FLASHCARDS ====================

  Future<Map<String, dynamic>> generateFlashcards(
    String filePath, {
    int numCards = 5,
  }) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/flashcards?num_cards=$numCards'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Flashcard generation failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Flashcard generation error: $e');
    }
  }

  // ==================== MCQ ====================

  Future<Map<String, dynamic>> generateMCQ(
    String filePath, {
    int numQuestions = 3,
  }) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/mcq?num_questions=$numQuestions'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('MCQ generation failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('MCQ generation error: $e');
    }
  }

  // ==================== ANALYTICS ====================

  Future<Map<String, dynamic>> getAnalytics({String? filePath}) async {
    try {
      var uri = Uri.parse('$baseUrl/api/analytics');
      if (filePath != null) {
        uri = Uri.parse('$baseUrl/api/analytics?file_path=${Uri.encodeComponent(filePath)}');
      }

      var response = await http.get(uri);

      if (response.statusCode != 200) {
        throw Exception('Analytics failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Analytics error: $e');
    }
  }

  // ==================== EXPORT METHODS ====================

  Future<Map<String, dynamic>> exportPDF(
    String filePath,
    String language, {
    bool includeTimestamps = true,
  }) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/export/pdf?include_timestamps=$includeTimestamps'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
          'language': language,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Export failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Export error: $e');
    }
  }

  Future<Map<String, dynamic>> exportClean(String filePath, String language) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/export/clean'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
          'language': language,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Export failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Export error: $e');
    }
  }

  Future<Map<String, dynamic>> exportDOCX(
    String filePath,
    String language,
  ) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/export/docx'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
          'language': language,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Export failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Export error: $e');
    }
  }

  Future<Map<String, dynamic>> exportTranslated(
    String filePath,
    String language, {
    String targetLanguage = 'en',
  }) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/export/translated?target_language=$targetLanguage'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
          'language': language,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Translation failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Translation error: $e');
    }
  }

  Future<Map<String, dynamic>> exportSummary(
    String filePath,
    String language,
  ) async {
    try {
      var response = await http.post(
        Uri.parse('$baseUrl/api/export/summary'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'file_path': filePath,
          'language': language,
        }),
      );

      if (response.statusCode != 200) {
        throw Exception('Export failed: ${response.statusCode}');
      }

      return json.decode(response.body);
    } catch (e) {
      throw Exception('Export error: $e');
    }
  }
}