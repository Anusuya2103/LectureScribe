# backend/app/services/transcriber.py
"""
Transcription service using OpenAI Whisper.
"""
import os
import whisper
import torch
import re
from typing import Optional, Dict, Any, List
from ..config import config
from .audio_processor import AudioProcessor


class TamilTranscriber:
    """Tamil transcriber using OpenAI Whisper (sequential only)."""
    
    def __init__(self, model_name: str = "large"):
        """
        Initialize Tamil transcriber.
        
        Args:
            model_name: 'base', 'small', 'medium', 'large'
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model."""
        try:
            print(f"Loading Whisper model: {self.model_name} (for Tamil)")
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"✅ Model loaded on {self.device}!")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def transcribe_tamil(self, audio_path: str) -> Dict[str, Any]:
        """Transcribe Tamil audio."""
        if self.model is None:
            raise RuntimeError("Model not loaded.")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            print(f"Transcribing: {audio_path}")
            print(f"Using model: {self.model_name}")
            
            result = self.model.transcribe(
                audio_path,
                language="ta",
                task="transcribe",
                temperature=0.0,
                verbose=True,
                fp16=False if self.device == "cpu" else True,
                compression_ratio_threshold=2.4,
                logprob_threshold=-1.0,
                no_speech_threshold=0.6,
                condition_on_previous_text=False,
                word_timestamps=True
            )
            
            # Clean up
            cleaned_text = self._clean_transcription(result.get('text', ''))
            
            return {
                'text': cleaned_text,
                'segments': result.get('segments', []),
                'language': 'ta',
                'duration': result.get('duration', 0)
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")
    
    def _clean_transcription(self, text: str) -> str:
        """Clean up transcription text."""
        if not text:
            return ""
        
        text = ' '.join(text.split())
        
        # Remove duplicate sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        unique_sentences = []
        seen = set()
        for sent in sentences:
            sent = sent.strip()
            if sent and sent not in seen:
                unique_sentences.append(sent)
                seen.add(sent)
        
        text = ' '.join(unique_sentences)
        
        # Fix mathematical expressions
        text = re.sub(r'\bdyc\b', 'dy/dx', text)
        text = re.sub(r'\bdxc\b', 'dx', text)
        text = re.sub(r'\bxq\b', 'x', text)
        
        return text.strip()


class EnglishTranscriber:
    """English transcriber."""
    
    def __init__(self, model_name: str = "base"):
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self._load_model()
    
    def _load_model(self):
        try:
            print(f"Loading Whisper model: {self.model_name} (for English)")
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"✅ Model loaded on {self.device}!")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def transcribe_english(self, audio_path: str) -> Dict[str, Any]:
        if self.model is None:
            raise RuntimeError("Model not loaded.")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        try:
            result = self.model.transcribe(
                audio_path,
                language="en",
                task="transcribe",
                fp16=False if self.device == "cpu" else True,
                temperature=0.0,
                verbose=True,
                condition_on_previous_text=False
            )
            
            return {
                'text': result.get('text', ''),
                'segments': result.get('segments', []),
                'language': 'en',
                'duration': result.get('duration', 0)
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")


# ==================== HuggingFaceTranscriber (Compatibility) ====================

class HuggingFaceTranscriber:
    """
    Compatible transcriber that uses OpenAI Whisper.
    Kept for backward compatibility with existing code.
    """
    
    def __init__(self, model_name: Optional[str] = None, language: str = "auto"):
        self.language = language
        self.model_name = model_name or "base"
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model."""
        try:
            print(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"✅ Model loaded on {self.device}!")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def transcribe(self, audio_path: str, language: Optional[str] = None) -> Dict[str, Any]:
        """Transcribe audio file."""
        if self.model is None:
            raise RuntimeError("Model not loaded.")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Determine language
        if language is None:
            language = self.language
        
        # Auto-detect from filename
        if language == "auto":
            filename = os.path.basename(audio_path).lower()
            if 'tamil' in filename or 'ta_' in filename:
                language = 'ta'
            else:
                language = 'en'
        
        try:
            result = self.model.transcribe(
                audio_path,
                language=language if language != "auto" else None,
                task="transcribe",
                fp16=False if self.device == "cpu" else True,
                temperature=0.0,
                verbose=True,
                condition_on_previous_text=False
            )
            
            # Clean up transcription
            text = result.get('text', '')
            text = ' '.join(text.split())
            
            return {
                'text': text,
                'segments': result.get('segments', []),
                'language': result.get('language', language),
                'duration': result.get('duration', 0)
            }
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")


# For backward compatibility
TamilTranscriber = TamilTranscriber
EnglishTranscriber = EnglishTranscriber