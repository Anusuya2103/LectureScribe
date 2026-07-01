# backend/app/services/diarizer.py
from typing import List, Dict

class Diarizer:
    """Speaker diarization service - using fallback for stability."""
    
    def __init__(self, model_name: str = "pyannote/speaker-diarization"):
        self.model_name = model_name
        self.pipeline = None
        print("⚠️ Using fallback diarization (no speaker identification)")
        print("All speech will be treated as coming from one speaker")
    
    def diarize(self, audio_path: str) -> List[Dict]:
        """Perform speaker diarization with fallback."""
        return self._fallback_diarize(audio_path)
    
    def _fallback_diarize(self, audio_path: str) -> List[Dict]:
        """Simple fallback diarization."""
        return [{
            'start': 0,
            'end': 60,
            'speaker': 'SPEAKER_00'
        }]

# Alias for backward compatibility
HuggingFaceDiarizer = Diarizer