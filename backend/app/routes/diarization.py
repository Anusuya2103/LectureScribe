# backend/app/services/diarizer.py
import torch
from typing import List, Dict, Optional
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the backend directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

class Diarizer:
    """Speaker diarization service."""
    
    def __init__(self, model_name: str = "pyannote/speaker-diarization"):
        self.model_name = model_name
        self.pipeline = None
        self._load_model()
    
    def _load_model(self):
        """Load the diarization model."""
        try:
            print(f"Loading diarization model: {self.model_name}")
            from pyannote.audio import Pipeline
            
            # Load token from environment
            hf_token = os.getenv("HUGGINGFACE_TOKEN")
            
            if hf_token:
                print(f"✅ Using Hugging Face token (starts with: {hf_token[:8]}...)")
                self.pipeline = Pipeline.from_pretrained(
                    self.model_name,
                    use_auth_token=hf_token
                )
            else:
                print("❌ No Hugging Face token found.")
                print(f"Looking for .env at: {env_path}")
                print("Using fallback diarization...")
                self.pipeline = None
                return
            
            # Send to GPU if available
            if torch.cuda.is_available():
                self.pipeline.to(torch.device("cuda"))
            
            print("✅ Diarization model loaded successfully!")
            
        except ImportError as e:
            print(f"Pyannote not installed: {e}")
            print("Falling back to simple diarization...")
            self.pipeline = None
        except Exception as e:
            print(f"Error loading diarization model: {e}")
            print("Falling back to simple diarization...")
            self.pipeline = None
    
    def diarize(self, audio_path: str) -> List[Dict]:
        """Perform speaker diarization on audio file."""
        if self.pipeline is None:
            return self._fallback_diarize(audio_path)
        
        try:
            diarization = self.pipeline(audio_path)
            
            segments = []
            for turn, _, speaker in diarization.itertracks(yield_label=True):
                segments.append({
                    'start': turn.start,
                    'end': turn.end,
                    'speaker': speaker
                })
            
            return segments
        except Exception as e:
            print(f"Diarization failed: {e}")
            return self._fallback_diarize(audio_path)
    
    def _fallback_diarize(self, audio_path: str) -> List[Dict]:
        """Simple fallback diarization."""
        print(f"Using fallback diarization for: {audio_path}")
        return [{
            'start': 0,
            'end': 60,
            'speaker': 'SPEAKER_00'
        }]

# Alias for backward compatibility
HuggingFaceDiarizer = Diarizer