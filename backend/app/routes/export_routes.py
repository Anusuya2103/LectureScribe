# backend/app/routes/export_routes.py
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services.export_service import ExportService

router = APIRouter(prefix="/api/export", tags=["Export"])
export_service = ExportService()

@router.post("/clean/{transcript_id}")
async def export_clean_transcript(
    transcript_id: str,
    include_timestamps: bool = False
):
    """Export transcript without timestamps."""
    try:
        # Get transcript from database
        # ...
        
        if include_timestamps:
            output_path = export_service.export_pdf(transcript, segments, metadata, transcript_id)
        else:
            output_path = export_service.export_without_timestamps(transcript, metadata, transcript_id)
        
        return {
            "status": "success",
            "download_url": f"/exports/{output_path}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translated/{transcript_id}")
async def export_translated_transcript(
    transcript_id: str,
    target_language: str = "en",
    include_original: bool = True
):
    """Export transcript with translation."""
    try:
        # Get transcript from database
        # ...
        
        result = export_service.export_tamil_with_translation(
            transcript, segments, metadata, transcript_id,
            translate_to_english=(target_language == "en")
        )
        
        return {
            "status": "success",
            "files": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/topic-summary/{transcript_id}")
async def export_topic_summary(transcript_id: str):
    """Export topic-wise summary."""
    try:
        # Get transcript from database
        # ...
        
        output_path = export_service.export_topic_summary(
            transcript, segments, metadata, transcript_id
        )
        
        return {
            "status": "success",
            "download_url": f"/exports/{output_path}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary/{transcript_id}")
async def get_topic_summary(transcript_id: str):
    """Get topic-wise summary as JSON."""
    try:
        # Get transcript from database
        # ...
        
        summary_data = export_service.generate_topic_summary(transcript, segments)
        
        return {
            "status": "success",
            "data": summary_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))