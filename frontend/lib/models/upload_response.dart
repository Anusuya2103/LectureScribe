class UploadResponse {
  final String fileId;
  final String filename;
  final String path;
  final int size;
  final String contentType;

  UploadResponse({
    required this.fileId,
    required this.filename,
    required this.path,
    required this.size,
    required this.contentType,
  });

  factory UploadResponse.fromJson(Map<String, dynamic> json) {
    return UploadResponse(
      fileId: json['file_id']?.toString() ?? '',
      filename: json['filename']?.toString() ?? '',
      path: json['path']?.toString() ?? '',
      size: json['size'] is int ? json['size'] : 0,
      contentType: json['content_type']?.toString() ?? '',
    );
  }
}