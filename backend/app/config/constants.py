"""
Application constants.
"""
from pathlib import Path

# Application Info
APP_NAME = "Classroom Minutes Generator"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "AI-powered classroom documentation system"

# File Constants
MAX_FILENAME_LENGTH = 255
CHUNK_SIZE = 8192  # For file reading

# Audio Constants
SAMPLE_RATE = 16000  # 16kHz for Whisper
MAX_AUDIO_DURATION = 7200  # 2 hours in seconds

# Transcription Constants
VAD_THRESHOLD = 0.5
MIN_SPEECH_DURATION = 0.3  # seconds
MAX_SILENCE_DURATION = 0.5  # seconds

# Summarization Constants
MIN_SUMMARY_LENGTH = 50
MAX_SUMMARY_LENGTH = 500
SUMMARY_TEMPERATURE = 0.3

# Speaker Diarization Constants
MIN_SPEAKERS = 2
MAX_SPEAKERS = 10
DIARIZATION_THRESHOLD = 0.5

# Tamil Language
TAMIL_UNICODE_RANGE = range(0x0B80, 0x0BFF + 1)
TAMIL_SCRIPT_PATTERN = r'[\u0B80-\u0BFF]'

# Response Messages
class Messages:
    FILE_UPLOAD_SUCCESS = "File uploaded successfully"
    FILE_UPLOAD_ERROR = "Error uploading file"
    FILE_NOT_FOUND = "File not found"
    TRANSCRIPTION_SUCCESS = "Transcription completed"
    TRANSCRIPTION_ERROR = "Error in transcription"
    SUMMARIZATION_SUCCESS = "Summary generated successfully"
    SUMMARIZATION_ERROR = "Error in summarization"
    DIARIZATION_SUCCESS = "Speaker diarization completed"
    DIARIZATION_ERROR = "Error in speaker diarization"
    PROCESSING_SUCCESS = "Processing completed"
    PROCESSING_ERROR = "Error in processing"