class ProcessingError(Exception):
    pass

class AudioProcessingError(ProcessingError):
    pass

class TranscriptionError(ProcessingError):
    pass

class SummarizationError(ProcessingError):
    pass