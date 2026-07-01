"""
Database models for the application.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.sql import func
from .connection import Base

class Lecture(Base):
    """Model for lecture recordings."""
    __tablename__ = "lectures"
    
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String(50), unique=True, index=True)
    filename = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    content_type = Column(String(100))
    
    status = Column(String(50), default="uploaded")
    
    duration = Column(Float, nullable=True)
    language = Column(String(10), nullable=True)
    speaker_count = Column(Integer, nullable=True)
    
    transcript = Column(Text, nullable=True)
    summary = Column(Text, nullable=True)
    structured_summary = Column(JSON, nullable=True)
    labeled_transcript = Column(Text, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    error_message = Column(Text, nullable=True)

class SpeakerSegment(Base):
    """Model for speaker segments in a lecture."""
    __tablename__ = "speaker_segments"
    
    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, index=True)
    speaker = Column(String(50))
    text = Column(Text)
    start_time = Column(Float)
    end_time = Column(Float)
    confidence = Column(Float, nullable=True)

class Question(Base):
    """Model for generated questions."""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    lecture_id = Column(Integer, index=True)
    question = Column(Text)
    answer = Column(Text)
    type = Column(String(50))
    options = Column(JSON, nullable=True)
    timestamp = Column(Float, nullable=True)

class ProcessingJob(Base):
    """Model for tracking async processing jobs."""
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String(50), unique=True, index=True)
    lecture_id = Column(Integer, index=True)
    task_type = Column(String(50))
    status = Column(String(50), default="pending")
    progress = Column(Integer, default=0)
    result_path = Column(String(500), nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())