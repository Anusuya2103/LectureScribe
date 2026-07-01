# backend/app/routes/advanced_features.py
from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import Optional
import os

from ..services.rag_chat import RAGChatService
from ..services.export_service import ExportService
from ..services.action_extractor import ActionItemExtractor
from ..services.topic_segmenter import TopicSegmenter
from ..services.flashcard_generator import FlashcardGenerator
from ..services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/advanced", tags=["Advanced Features"])

# Initialize services
rag_service = RAGChatService()
export_service = ExportService()
action_extractor = ActionItemExtractor()
topic_segmenter = TopicSegmenter()
flashcard_generator = FlashcardGenerator()
analytics_service = AnalyticsService()

@router.post("/chat/{transcript_id}")
async def chat_with_transcript(transcript_id: str, question: str):
    """Chat with transcript using RAG."""
    try:
        result = rag_service.chat(transcript_id, question)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/export/{transcript_id}")
async def export_transcript(
    transcript_id: str,
    format: str = "pdf",
    include_timestamps: bool = True
):
    """Export transcript in specified format."""
    try:
        # Get transcript from database
        # ...
        
        if format == "pdf":
            output_path = export_service.export_pdf(transcript, segments, transcript_id)
        elif format == "docx":
            output_path = export_service.export_docx(transcript, segments, transcript_id)
        else:
            raise HTTPException(status_code=400, detail="Unsupported format")
        
        return {"status": "success", "download_url": f"/exports/{output_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/actions/{transcript_id}")
async def extract_actions(transcript_id: str):
    """Extract action items from transcript."""
    try:
        # Get transcript from database
        # ...
        actions = action_extractor.extract_actions(transcript)
        return {"status": "success", "actions": actions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/flashcards/{transcript_id}")
async def generate_flashcards(
    transcript_id: str,
    num_cards: int = 10,
    include_mcq: bool = True
):
    """Generate flashcards and MCQs."""
    try:
        # Get transcript from database
        # ...
        flashcards = flashcard_generator.generate_flashcards(transcript, num_cards)
        mcqs = flashcard_generator.generate_mcq(transcript, num_cards // 2) if include_mcq else []
        
        return {
            "status": "success",
            "flashcards": flashcards,
            "mcqs": mcqs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analytics/{transcript_id}")
async def get_analytics(transcript_id: str):
    """Get lecture analytics."""
    try:
        # Get transcript from database
        # ...
        analytics = analytics_service.generate_analytics(transcript, segments)
        return {"status": "success", "analytics": analytics}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))