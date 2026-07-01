"""
Main FastAPI application.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from backend directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

# Print token status for debugging
token = os.getenv("HUGGINGFACE_TOKEN")
if token:
    print(f"✅ Hugging Face token loaded successfully (starts with: {token[:8]}...)")
else:
    print("⚠️ No Hugging Face token found in .env file")
    print(f"Looking for .env at: {env_path}")

from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import shutil
from datetime import datetime
from typing import Optional, List
import json

from .config import config
from .schemas import (
    UploadResponse, TranscriptionRequest, TranscriptionResponse,
    SummarizationRequest, SummaryResponse,
    DiarizationRequest, DiarizationResponse,
    QuestionGenerationRequest, QuestionResponse,
    StatusResponse
)
from .services.pipeline import ProcessingPipeline
from .services.export_service import ExportService
from .services.utils import generate_file_id, safe_filename, format_transcript
from .db.connection import get_db, init_db
from .db.repository import LectureRepository, JobRepository

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Classroom Minutes Generator",
    description="AI-powered classroom documentation system using HuggingFace models",
    version="1.0.0"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://localhost:8001",
        "http://localhost:8080",
        "http://127.0.0.1:8000",
        "http://127.0.0.1:8001",
        "http://127.0.0.1:8080",
        "http://localhost:52000",
        "http://127.0.0.1:52000",
        "http://localhost:53000",
        "http://127.0.0.1:53000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

# Create pipeline instance
pipeline = ProcessingPipeline()

# Create export service
export_service = ExportService()

# ==================== CACHE SYSTEM ====================
# Simple in-memory cache for processed results to avoid model reloading
process_cache = {}
MAX_CACHE_SIZE = 10  # Maximum number of cached results

def get_cached_result(file_path: str, language: str):
    """Get cached result if available."""
    cache_key = f"{file_path}_{language}"
    return process_cache.get(cache_key)

def set_cached_result(file_path: str, language: str, result: dict):
    """Store result in cache."""
    cache_key = f"{file_path}_{language}"
    
    # If cache is full, remove oldest entry
    if len(process_cache) >= MAX_CACHE_SIZE:
        # Remove first item (oldest)
        oldest_key = next(iter(process_cache))
        process_cache.pop(oldest_key)
        print(f"🗑️ Removed oldest cache entry: {oldest_key}")
    
    process_cache[cache_key] = result
    print(f"📦 Cached result for: {file_path}")

# Create directories
upload_dir = Path(config.upload_dir)
transcript_dir = Path(config.transcript_dir)
summary_dir = Path(config.summary_dir)
temp_dir = Path(config.temp_dir)

os.makedirs(upload_dir, exist_ok=True)
os.makedirs(transcript_dir, exist_ok=True)
os.makedirs(summary_dir, exist_ok=True)
os.makedirs(temp_dir, exist_ok=True)
os.makedirs("exports", exist_ok=True)

# Update config with Path objects
config.upload_dir = upload_dir
config.transcript_dir = transcript_dir
config.summary_dir = summary_dir
config.temp_dir = temp_dir

# ==================== HEALTH & ROOT ====================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
async def root():
    """Root endpoint with all available endpoints."""
    return {
        "message": "Classroom Minutes Generator API",
        "version": "1.0.0",
        "endpoints": {
            "/docs": "API documentation",
            "/health": "Health check",
            "/api/upload": "Upload audio file",
            "/api/transcribe": "Transcribe audio",
            "/api/summarize": "Generate summary",
            "/api/diarize": "Speaker diarization",
            "/api/process": "Full processing pipeline",
            "/api/questions": "Generate questions",
            "/api/export/pdf": "Export as PDF",
            "/api/export/docx": "Export as DOCX",
            "/api/export/translated": "Export with translation",
            "/api/export/summary": "Export summary",
            "/api/export/clean": "Export without timestamps",
            "/api/export/bilingual": "Export bilingual PDF (Tamil + English)",
            "/api/chat": "Chat with transcript (RAG)",
            "/api/actions": "Extract action items",
            "/api/topics": "Topic segmentation",
            "/api/flashcards": "Generate flashcards",
            "/api/mcq": "Generate multiple choice questions",
            "/api/analytics": "Lecture analytics",
            "/api/status/{job_id}": "Get processing status"
        }
    }

# ==================== UPLOAD ====================

@app.post("/api/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload an audio file for processing."""
    if file.content_type and file.content_type not in config.allowed_mime_types:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file.content_type} not supported. Supported types: {config.allowed_mime_types}"
        )
    
    file_id = generate_file_id(file.filename)
    safe_name = safe_filename(file.filename)
    filename = f"{file_id}_{safe_name}"
    
    file_path = upload_dir / filename
    file_size = 0
    
    try:
        contents = await file.read()
        file_size = len(contents)
        
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        try:
            db = next(get_db())
            repo = LectureRepository(db)
            lecture = repo.create(
                file_id=file_id,
                filename=file.filename,
                file_path=str(file_path),
                file_size=file_size,
                content_type=file.content_type or "audio/mpeg"
            )
        except Exception as db_error:
            print(f"Database error: {db_error}")
        
        return UploadResponse(
            message="File uploaded successfully",
            file_id=file_id,
            filename=file.filename,
            path=str(file_path),
            size=file_size,
            content_type=file.content_type or "audio/mpeg"
        )
        
    except Exception as e:
        if file_path.exists():
            os.remove(file_path)
        print(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# ==================== CORE PROCESSING ====================

@app.post("/api/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(request: TranscriptionRequest):
    """Transcribe an audio file."""
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        result = pipeline.process_only_transcription(str(audio_path), language=request.language)
        
        return TranscriptionResponse(
            status="success",
            transcript=result['text'],
            segments=result.get('segments', []),
            language=result.get('language', request.language),
            saved_to=result.get('saved_to', ''),
            duration=result.get('duration', 0)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription failed: {str(e)}")

@app.post("/api/summarize", response_model=SummaryResponse)
async def summarize_transcript(request: SummarizationRequest):
    """Generate summary from transcript."""
    transcript_path = Path(request.transcript_path)
    if not transcript_path.exists():
        raise HTTPException(status_code=404, detail="Transcript file not found")
    
    try:
        result = pipeline.process_only_summarization(str(transcript_path))
        
        return SummaryResponse(
            status="success",
            summary=result['summary'],
            structured=result.get('structured_minutes', {}),
            saved_to=result.get('saved_to', '')
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summarization failed: {str(e)}")

@app.post("/api/process")
async def process_full(request: TranscriptionRequest):
    """Run the full processing pipeline with caching."""
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Check cache first
        cached = get_cached_result(str(audio_path), request.language)
        if cached:
            print("📦 Returning cached result")
            return cached
        
        result = pipeline.process_full_pipeline(str(audio_path), language=request.language)
        
        if result['status'] == 'error':
            raise Exception(result.get('error', 'Pipeline error'))
        
        response_data = {
            "status": "success",
            "transcript": result.get('transcript'),
            "segments": result.get('segments', []),
            "saved_to": result.get('saved_to'),
            "summary": result.get('summary'),
            "structured_minutes": result.get('structured_minutes'),
            "questions": result.get('questions', []),
            "speakers": result.get('speakers', []),
            "metadata": result.get('metadata', {})
        }
        
        # Store in cache
        set_cached_result(str(audio_path), request.language, response_data)
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/diarize", response_model=DiarizationResponse)
async def diarize_audio(request: DiarizationRequest):
    """Perform speaker diarization."""
    audio_path = Path(request.audio_path)
    transcript_path = Path(request.transcript_path)
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    if not transcript_path.exists():
        raise HTTPException(status_code=404, detail="Transcript file not found")
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        diarization_result = pipeline.diarizer.diarize(str(audio_path))
        
        speakers = []
        if diarization_result:
            speakers = list(set([seg.get('speaker', 'Unknown') for seg in diarization_result]))
        
        if diarization_result:
            labeled_segments = []
            for seg in diarization_result:
                labeled_segments.append({
                    'speaker': seg.get('speaker', 'Unknown'),
                    'text': transcript,
                    'start': seg.get('start', 0),
                    'end': seg.get('end', 0)
                })
            labeled_transcript = format_transcript(labeled_segments)
        else:
            labeled_transcript = transcript
        
        return DiarizationResponse(
            status="success",
            labeled_transcript=labeled_transcript,
            speakers=speakers,
            saved_to=str(transcript_path)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Diarization failed: {str(e)}")

@app.post("/api/questions", response_model=QuestionResponse)
async def generate_questions(request: QuestionGenerationRequest):
    """Generate questions from transcript."""
    transcript_path = Path(request.transcript_path)
    if not transcript_path.exists():
        raise HTTPException(status_code=404, detail="Transcript file not found")
    
    try:
        questions = pipeline.question_generator.generate_questions(
            str(transcript_path),
            num_questions=request.num_questions
        )
        
        return QuestionResponse(
            status="success",
            questions=questions,
            saved_to=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Question generation failed: {str(e)}")

# ==================== EXPORT FEATURES ====================

@app.post("/api/export/pdf")
async def export_pdf(request: TranscriptionRequest, include_timestamps: bool = True):
    """Export transcript as PDF using cached or processed transcript."""
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Try to get from cache first
        cached = get_cached_result(str(audio_path), request.language)
        
        if cached:
            print("📦 Using cached data for PDF export")
            transcript = cached.get('transcript', '')
            segments = cached.get('segments', [])
            if not segments:
                segments = [{'text': transcript, 'start': 0, 'end': 0}]
            metadata = cached.get('metadata', {'duration': 0})
        else:
            print("🔄 Processing for PDF export")
            result = pipeline.process_only_transcription(str(audio_path), language=request.language)
            transcript = result['text']
            segments = result.get('segments', [])
            if not segments:
                segments = [{'text': transcript, 'start': 0, 'end': result.get('duration', 0)}]
            metadata = {'duration': result.get('duration', 0)}
        
        filename = audio_path.stem
        
        if include_timestamps:
            output_path = export_service.export_pdf(transcript, segments, metadata, filename)
        else:
            output_path = export_service.export_pdf_without_timestamps(transcript, metadata, filename)
        
        return {
            "status": "success",
            "download_url": f"/exports/{Path(output_path).name}",
            "message": "PDF exported successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.post("/api/export/docx")
async def export_docx(request: TranscriptionRequest):
    """Export transcript as DOCX using cached or processed transcript."""
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Try to get from cache first
        cached = get_cached_result(str(audio_path), request.language)
        
        if cached:
            print("📦 Using cached data for DOCX export")
            transcript = cached.get('transcript', '')
            segments = cached.get('segments', [])
            if not segments:
                segments = [{'text': transcript, 'start': 0, 'end': 0}]
            metadata = cached.get('metadata', {'duration': 0})
        else:
            print("🔄 Processing for DOCX export")
            result = pipeline.process_only_transcription(str(audio_path), language=request.language)
            transcript = result['text']
            segments = result.get('segments', [])
            if not segments:
                segments = [{'text': transcript, 'start': 0, 'end': result.get('duration', 0)}]
            metadata = {'duration': result.get('duration', 0)}
        
        filename = audio_path.stem
        
        output_path = export_service.export_docx(transcript, segments, metadata, filename)
        
        return {
            "status": "success",
            "download_url": f"/exports/{Path(output_path).name}",
            "message": "DOCX exported successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.post("/api/export/clean")
async def export_clean(request: TranscriptionRequest):
    """Export transcript without timestamps."""
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Try to get from cache first
        cached = get_cached_result(str(audio_path), request.language)
        
        if cached:
            print("📦 Using cached data for Clean PDF export")
            transcript = cached.get('transcript', '')
            metadata = cached.get('metadata', {'duration': 0})
        else:
            print("🔄 Processing for Clean PDF export")
            result = pipeline.process_only_transcription(str(audio_path), language=request.language)
            transcript = result['text']
            metadata = {'duration': result.get('duration', 0)}
        
        filename = audio_path.stem
        
        output_path = export_service.export_pdf_without_timestamps(transcript, metadata, filename)
        
        return {
            "status": "success",
            "download_url": f"/exports/{Path(output_path).name}",
            "message": "Clean PDF exported successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@app.post("/api/export/translated")
async def export_translated(request: TranscriptionRequest, target_language: str = "en"):
    """Export transcript with translation."""
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Try to get from cache first
        cached = get_cached_result(str(audio_path), request.language)
        
        if cached:
            print("📦 Using cached data for Translation export")
            transcript = cached.get('transcript', '')
            segments = cached.get('segments', [])
            if not segments:
                segments = [{'text': transcript, 'start': 0, 'end': 0}]
            metadata = cached.get('metadata', {'duration': 0})
        else:
            print("🔄 Processing for Translation export")
            result = pipeline.process_only_transcription(str(audio_path), language=request.language)
            transcript = result['text']
            segments = result.get('segments', [])
            if not segments:
                segments = [{'text': transcript, 'start': 0, 'end': result.get('duration', 0)}]
            metadata = {'duration': result.get('duration', 0)}
        
        filename = audio_path.stem
        
        output = export_service.export_translated(
            transcript, segments, metadata, filename, target_language
        )
        
        return {
            "status": "success",
            "files": output,
            "message": f"Translated to {target_language} successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")

@app.post("/api/export/summary")
async def export_summary(request: TranscriptionRequest):
    """Export summary as DOCX."""
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Try to get from cache first
        cached = get_cached_result(str(audio_path), request.language)
        
        if cached:
            print("📦 Using cached data for Summary export")
            summary = cached.get('summary', 'No summary available')
            structured_minutes = cached.get('structured_minutes', {})
        else:
            print("🔄 Processing for Summary export")
            result = pipeline.process_full_pipeline(str(audio_path), language=request.language)
            summary = result.get('summary', 'No summary available')
            structured_minutes = result.get('structured_minutes', {})
        
        filename = audio_path.stem
        
        output_path = export_service.export_summary(summary, structured_minutes, filename)
        
        return {
            "status": "success",
            "download_url": f"/exports/{Path(output_path).name}",
            "message": "Summary exported successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

# ==================== BILINGUAL EXPORT ====================

@app.post("/api/export/bilingual")
async def export_bilingual(request: TranscriptionRequest):
    """
    Export bilingual transcript (Tamil + English side-by-side).
    """
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        # Try to get from cache first
        cached = get_cached_result(str(audio_path), request.language)
        
        if cached:
            print("📦 Using cached data for Bilingual export")
            # For bilingual, we need both Tamil and English
            # If cache only has one, we need to process again
            transcript_tamil = cached.get('transcript_tamil', cached.get('transcript', ''))
            transcript_english = cached.get('transcript_english', cached.get('transcript', ''))
            
            # If we don't have both, process fresh
            if not transcript_tamil or not transcript_english:
                print("🔄 Cache missing bilingual data, processing fresh...")
                result = pipeline.process_full_pipeline(str(audio_path), language=request.language)
                transcript_tamil = result.get('transcript_tamil', result.get('transcript', ''))
                transcript_english = result.get('transcript_english', result.get('transcript', ''))
            else:
                # Use cached metadata
                metadata = cached.get('metadata', {'duration': 0})
        else:
            print("🔄 Processing for Bilingual export...")
            result = pipeline.process_full_pipeline(str(audio_path), language=request.language)
            transcript_tamil = result.get('transcript_tamil', result.get('transcript', ''))
            transcript_english = result.get('transcript_english', result.get('transcript', ''))
            metadata = result.get('metadata', {'duration': 0})
        
        filename = audio_path.stem
        
        output_path = export_service.export_bilingual_pdf(
            transcript_tamil, 
            transcript_english, 
            metadata, 
            filename
        )
        
        return {
            "status": "success",
            "download_url": f"/exports/{Path(output_path).name}",
            "message": "Bilingual PDF exported successfully (Tamil + English)"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Bilingual export failed: {str(e)}")

# ==================== ADVANCED FEATURES ====================

@app.post("/api/chat")
async def chat_with_transcript(
    transcript_id: str,
    question: str,
    file_path: Optional[str] = None
):
    """
    Chat with transcript using RAG (Retrieval Augmented Generation).
    """
    try:
        return {
            "status": "success",
            "question": question,
            "answer": "This is a placeholder response. RAG chat feature will be implemented with ChromaDB.",
            "sources": ["transcript_segment_1", "transcript_segment_2"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")

@app.post("/api/actions")
async def extract_actions(request: TranscriptionRequest):
    """
    Extract action items from transcript.
    """
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        result = pipeline.process_full_pipeline(str(audio_path), language=request.language)
        transcript = result.get('transcript', '')
        
        import re
        actions = []
        patterns = [
            r'(?:should|must|need to|has to|will|shall)\s+(\w+\s+[\w\s]+)',
            r'(?:action item|next step|todo|task):\s*([^\n]+)'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, transcript, re.IGNORECASE)
            for match in matches:
                actions.append({
                    'description': match.strip(),
                    'priority': 'medium',
                    'deadline': 'TBD'
                })
        
        return {
            "status": "success",
            "actions": actions[:10],
            "count": len(actions[:10])
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Action extraction failed: {str(e)}")

@app.post("/api/topics")
async def segment_topics(request: TranscriptionRequest):
    """
    Segment transcript into topics.
    """
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        result = pipeline.process_full_pipeline(str(audio_path), language=request.language)
        segments = result.get('segments', [])
        
        topics = []
        if segments:
            total_duration = segments[-1].get('end', 0) if segments else 0
            topic_count = 3
            duration_per_topic = total_duration / topic_count if topic_count > 0 else 60
            
            for i in range(topic_count):
                start_time = i * duration_per_topic
                end_time = (i + 1) * duration_per_topic
                
                topic_segments = [s for s in segments if s.get('start', 0) >= start_time and s.get('start', 0) < end_time]
                topic_text = ' '.join([s.get('text', '') for s in topic_segments])
                
                if topic_text:
                    topics.append({
                        'topic': f"Topic {i+1}",
                        'text': topic_text[:200] + "..." if len(topic_text) > 200 else topic_text,
                        'start': start_time,
                        'end': end_time
                    })
        
        return {
            "status": "success",
            "topics": topics,
            "count": len(topics)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Topic segmentation failed: {str(e)}")

@app.post("/api/flashcards")
async def generate_flashcards(
    request: TranscriptionRequest,
    num_cards: int = Query(5, ge=1, le=20)
):
    """
    Generate flashcards from transcript.
    """
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        result = pipeline.process_full_pipeline(str(audio_path), language=request.language)
        transcript = result.get('transcript', '')
        
        import re
        sentences = re.split(r'[.!?]+', transcript)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        flashcards = []
        for i, sentence in enumerate(sentences[:num_cards]):
            if ' is ' in sentence:
                parts = sentence.split(' is ', 1)
                question = f"What is {parts[0][:50]}...?"
            else:
                question = f"What is the meaning of: {sentence[:50]}...?"
            
            flashcards.append({
                'id': i + 1,
                'question': question,
                'answer': sentence,
                'source': f'Segment {i+1}'
            })
        
        return {
            "status": "success",
            "flashcards": flashcards,
            "count": len(flashcards)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flashcard generation failed: {str(e)}")

@app.post("/api/mcq")
async def generate_mcq(
    request: TranscriptionRequest,
    num_questions: int = Query(3, ge=1, le=10)
):
    """
    Generate multiple choice questions from transcript.
    """
    audio_path = Path(request.file_path)
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    try:
        result = pipeline.process_full_pipeline(str(audio_path), language=request.language)
        transcript = result.get('transcript', '')
        
        import re
        sentences = re.split(r'[.!?]+', transcript)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        
        mcqs = []
        for i, sentence in enumerate(sentences[:num_questions]):
            mcqs.append({
                'id': i + 1,
                'question': f"What is the main idea of: {sentence[:80]}...?",
                'options': [
                    sentence[:100] + "...",
                    "This is a distractor option",
                    "Another distractor option",
                    "One more distractor option"
                ],
                'correct_answer': 0,
                'explanation': f"Based on the lecture: {sentence[:100]}..."
            })
        
        return {
            "status": "success",
            "mcqs": mcqs,
            "count": len(mcqs)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCQ generation failed: {str(e)}")

@app.get("/api/analytics")
async def get_analytics(
    transcript_id: Optional[str] = None,
    file_path: Optional[str] = None
):
    """
    Get lecture analytics.
    """
    try:
        if file_path:
            audio_path = Path(file_path)
            if not audio_path.exists():
                raise HTTPException(status_code=404, detail="Audio file not found")
            
            result = pipeline.process_full_pipeline(str(audio_path), language="auto")
            transcript = result.get('transcript', '')
            segments = result.get('segments', [])
        else:
            transcript = "Sample transcript for analytics"
            segments = []
        
        words = transcript.split()
        
        analytics = {
            'summary': {
                'total_words': len(words),
                'total_sentences': len(transcript.split('.')),
                'unique_words': len(set([w.lower() for w in words if len(w) > 3])),
                'avg_word_length': sum(len(w) for w in words) / max(len(words), 1)
            },
            'readability': {
                'flesch_score': 60 + (100 - min(100, len(words) / max(len(transcript.split('.')), 1) * 10)),
                'avg_words_per_sentence': len(words) / max(len(transcript.split('.')), 1)
            },
            'segments': {
                'count': len(segments),
                'duration': segments[-1].get('end', 0) if segments else 0
            },
            'top_keywords': _extract_keywords(transcript, 10),
            'sentiment': _analyze_sentiment(transcript)
        }
        
        return {
            "status": "success",
            "analytics": analytics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analytics failed: {str(e)}")

def _extract_keywords(text: str, limit: int = 10) -> List[str]:
    """Extract keywords from text."""
    import re
    from collections import Counter
    
    words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
    common_words = {'this', 'that', 'with', 'from', 'have', 'will', 'they', 'what', 'when', 'there', 'these', 'their', 'them', 'then', 'than', 'other', 'some', 'more', 'most', 'such', 'which', 'would', 'could', 'should', 'about', 'after', 'before', 'between', 'through', 'during', 'without', 'within', 'among', 'because', 'therefore', 'however', 'otherwise'}
    
    keywords = [w for w in words if w not in common_words]
    return [word for word, count in Counter(keywords).most_common(limit)]

def _analyze_sentiment(text: str) -> str:
    """Analyze sentiment of text."""
    positive_words = {'good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'brilliant', 'awesome', 'perfect', 'beautiful', 'nice', 'happy', 'love', 'best', 'better', 'important', 'valuable', 'helpful', 'useful', 'clear', 'easy', 'simple', 'understand'}
    negative_words = {'bad', 'poor', 'terrible', 'awful', 'horrible', 'worse', 'worst', 'difficult', 'hard', 'complex', 'confusing', 'unclear', 'problem', 'issue', 'error', 'wrong', 'fail', 'miss', 'lost', 'tough'}
    
    words = text.lower().split()
    positive_count = sum(1 for w in words if w in positive_words)
    negative_count = sum(1 for w in words if w in negative_words)
    
    if positive_count > negative_count * 1.5:
        return 'positive'
    elif negative_count > positive_count * 1.5:
        return 'negative'
    else:
        return 'neutral'

# ==================== STATUS ====================

@app.get("/api/status/{job_id}", response_model=StatusResponse)
async def get_status(job_id: str):
    """Get processing status."""
    try:
        db = next(get_db())
        repo = JobRepository(db)
        job = repo.get_by_id(job_id)
        
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
        
        return StatusResponse(
            status=job.status,
            progress=job.progress,
            message=job.error_message,
            result=None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ==================== FILE DOWNLOAD ====================

@app.get("/exports/{filename}")
async def download_export(filename: str):
    """Download exported file."""
    file_path = Path("exports") / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=str(file_path), filename=filename)

# ==================== FRONTEND ====================

frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="static")
    
    @app.get("/ui")
    async def serve_frontend():
        return FileResponse(str(frontend_path / "index.html"))

# ==================== RUN ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.port,
        reload=config.debug
    )