import 'package:file_picker/file_picker.dart';
import '../utils/constants.dart';

class AudioService {
  Future<PlatformFile?> pickAudioFile() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: AppConstants.allowedAudioExtensions
            .map((ext) => ext.replaceFirst('.', ''))
            .toList(),
      );

      if (result != null && result.files.isNotEmpty) {
        return result.files.first;
      }
      return null;
    } catch (e) {
      print('Error picking file: $e');
      return null;
    }
  }

  bool isSupportedFile(PlatformFile file) {
    var extension = file.extension?.toLowerCase() ?? '';
    return AppConstants.allowedAudioExtensions
        .map((ext) => ext.replaceFirst('.', ''))
        .contains(extension);
  }

  String? getFileName(PlatformFile file) {
    return file.name;
  }

  int? getFileSize(PlatformFile file) {
    return file.size;
  }
}