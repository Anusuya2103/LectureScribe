// lib/models/process_response.dart
class ProcessResponse {
  final String status;
  final String? transcript;
  final String? summary;
  final List<String>? questions;
  final Map<String, dynamic>? structuredMinutes;
  final List<Map<String, dynamic>>? speakers;
  final Map<String, dynamic>? metadata;
  final String? error;
  final String? savedTo;
  final List<Map<String, dynamic>>? segments;

  ProcessResponse({
    required this.status,
    this.transcript,
    this.summary,
    this.questions,
    this.structuredMinutes,
    this.speakers,
    this.metadata,
    this.error,
    this.savedTo,
    this.segments,
  });

  factory ProcessResponse.fromJson(Map<String, dynamic> json) {
    print('ProcessResponse JSON: $json');
    
    // Parse segments if available
    List<Map<String, dynamic>>? segments;
    if (json['segments'] != null) {
      segments = List<Map<String, dynamic>>.from(json['segments']);
    } else if (json['segments'] == null && json['transcript'] != null) {
      // Create a single segment from transcript
      segments = [{
        'text': json['transcript'],
        'start': 0,
        'end': json['duration'] ?? 0,
      }];
    }
    
    return ProcessResponse(
      status: json['status']?.toString() ?? 'error',
      transcript: json['transcript']?.toString(),
      summary: json['summary']?.toString(),
      questions: json['questions'] != null 
          ? List<String>.from(json['questions']) 
          : null,
      structuredMinutes: json['structured_minutes'],
      speakers: json['speakers'] != null
          ? List<Map<String, dynamic>>.from(json['speakers'])
          : null,
      metadata: json['metadata'],
      error: json['error']?.toString(),
      savedTo: json['saved_to']?.toString(),
      segments: segments,
    );
  }

  bool get isSuccess => status == 'success';
}