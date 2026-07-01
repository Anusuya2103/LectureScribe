"""
Summarization service using HuggingFace models.
"""
from typing import Optional
import re
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

from ..config import config


class HuggingFaceSummarizer:
    """Summarizer using HuggingFace models."""

    def __init__(self, model_name: Optional[str] = None):
        self.model_name = model_name or config.summarization_model
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        self.tokenizer = None
        self._load_model()

    def _load_model(self):
        try:
            print(f"Loading summarization model: {self.model_name}")
            # Load model and tokenizer directly
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            # Move to GPU if available
            if self.device == "cuda":
                self.model = self.model.to("cuda")
            
            print("Summarization model loaded successfully!")
        except Exception as e:
            print(f"Error loading summarization model: {e}")
            print("Using fallback summarization...")
            self.model = None
            self.tokenizer = None

    def summarize(self, text: str, max_length: int = 150, min_length: int = 30) -> str:
        """Generate a summary of the given text."""
        if not text or not text.strip():
            return ""

        # Truncate long texts
        text = text[:4096]

        if self.model and self.tokenizer:
            try:
                # Tokenize input
                inputs = self.tokenizer(
                    text, 
                    return_tensors="pt", 
                    max_length=1024, 
                    truncation=True
                )
                
                if self.device == "cuda":
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
                # Generate summary
                summary_ids = self.model.generate(
                    inputs["input_ids"],
                    max_length=max_length,
                    min_length=min_length,
                    num_beams=4,
                    early_stopping=True
                )
                
                # Decode summary
                summary = self.tokenizer.decode(
                    summary_ids[0], 
                    skip_special_tokens=True
                )
                
                return summary
            except Exception as e:
                print(f"Summarization error: {e}")

        # Fallback summarization
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        return ". ".join(sentences[:5]) if sentences else text[:500]


class StructuredMinutesGenerator:
    """Generate structured minutes from transcripts."""
    
    def __init__(self, summarizer=None):
        self.summarizer = summarizer
        self.sections = {
            "title": None,
            "date": None,
            "attendees": [],
            "agenda": [],
            "discussion": [],
            "decisions": [],
            "action_items": [],
            "next_meeting": None
        }
    
    def generate(self, transcript: str) -> dict:
        """
        Generate structured minutes from transcript.
        
        Args:
            transcript: The transcript text
            
        Returns:
            Dictionary with structured minutes
        """
        # Use summarizer if available
        summary = transcript
        if self.summarizer:
            try:
                summary = self.summarizer.summarize(transcript)
            except:
                summary = transcript[:500]
        
        # Placeholder implementation
        return {
            "title": "Meeting Minutes",
            "date": "2024-01-01",
            "attendees": ["Speaker 1", "Speaker 2"],
            "agenda": ["Item 1", "Item 2"],
            "discussion": summary if summary else transcript[:500],
            "decisions": ["Decision 1"],
            "action_items": ["Action 1"],
            "next_meeting": "2024-02-01"
        }