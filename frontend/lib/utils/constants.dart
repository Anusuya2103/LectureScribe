class AppConstants {
  static const String appName = 'Classroom Minutes';
  // Use 127.0.0.1 instead of localhost
  static const String apiBaseUrl = 'http://127.0.0.1:8000';
  static const int connectTimeout = 30000;
  static const int receiveTimeout = 300000;
  static const int maxFileSize = 500 * 1024 * 1024;

  static const List<String> allowedAudioExtensions = [
    '.mp3', '.wav', '.m4a', '.ogg', '.flac', '.aac'
  ];

  static const Map<String, String> languages = {
    'auto': 'Auto Detect',
    'en': 'English',
    'ta': 'Tamil',
  };
}