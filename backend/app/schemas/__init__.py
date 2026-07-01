"""
Pydantic schemas for request/response validation.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field

# ---------- Request Schemas ----------

class TranscriptionRequest(BaseModel):
    file_path: str = Field(..., description="Path to audio file")
    language: str = Field("auto", description="Language code (en, ta, auto)")
    task: str = Field("transcribe", description="transcribe or translate")
    word_timestamps: bool = Field(True, description="Include word timestamps")

class SummarizationRequest(BaseModel):
    transcript_path: str = Field(..., description="Path to transcript file")
    max_length: int = Field(500, ge=100, le=1000, description="Max summary length")
    min_length: int = Field(50, ge=20, le=200, description="Min summary length")

class DiarizationRequest(BaseModel):
    audio_path: str = Field(..., description="Path to audio file")
    transcript_path: str = Field(..., description="Path to transcript file")
    num_speakers: Optional[int] = Field(None, description="Number of speakers")

class QuestionGenerationRequest(BaseModel):
    transcript_path: str = Field(..., description="Path to transcript file")
    num_questions: int = Field(5, ge=1, le=20, description="Number of questions")
    question_types: List[str] = Field(
        ["short_answer", "mcq"],
        description="Types of questions to generate"
    )

# ---------- Response Schemas ----------

class UploadResponse(BaseModel):
    message: str
    file_id: str
    filename: str
    path: str
    size: int
    content_type: str

class TranscriptionResponse(BaseModel):
    status: str
    transcript: str
    segments: List[Dict[str, Any]]
    language: Optional[str] = None
    saved_to: str
    duration: Optional[float] = None

class SummaryResponse(BaseModel):
    status: str
    summary: str
    structured: Optional[Dict[str, Any]] = None
    saved_to: str

class DiarizationResponse(BaseModel):
    status: str
    labeled_transcript: str
    speakers: List[str]
    saved_to: str

class QuestionResponse(BaseModel):
    status: str
    questions: List[Dict[str, Any]]
    saved_to: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    progress: int
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None