"""
Application settings with environment variable validation.
"""
import os
from typing import Optional
from pathlib import Path
from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    """Application settings."""
    
    # HuggingFace
    huggingface_token: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./classroom_minutes.db"
    
    # Models
    whisper_model: str = "openai/whisper-base"  # English model
    asr_model: str = "openai/whisper-large"  # Tamil model (using same base model)
    summarization_model: str = "facebook/bart-large-cnn"
    diarization_model: str = "pyannote/speaker-diarization"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    cors_origins: list = [
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        "http://127.0.0.1:8080",
        "http://localhost:52000",   # Flutter web default
        "http://127.0.0.1:52000",
        "http://localhost:53000",
        "http://127.0.0.1:53000",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"  # Allow all for development (remove in production)
    ]
    
    # Allowed MIME types for upload
    allowed_mime_types: list = [
        "audio/mpeg",
        "audio/mp3",
        "audio/wav",
        "audio/x-wav",
        "audio/mp4",
        "audio/aac",
        "audio/ogg",
        "audio/flac",
        "audio/x-ms-wma",
        "audio/aiff",
        "application/octet-stream"  # For files without proper MIME type
    ]
    
    # File upload
    max_file_size: int = 500 * 1024 * 1024  # 500 MB
    
    # Directories
    upload_dir: str = "./data/raw"
    transcript_dir: str = "./data/transcripts"
    summary_dir: str = "./data/summaries"
    temp_dir: str = "./data/temp"
    
    # Logging
    log_level: str = "INFO"
    
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="allow"
    )

settings = Settings()
