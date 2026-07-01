from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from ..services.summarizer import LectureSummarizer

router = APIRouter()
summarizer = LectureSummarizer("ollama")  # or "openai"

class SummaryRequest(BaseModel):
    transcript_path: str

@router.post("/summarize")
async def create_summary(request: SummaryRequest):
    """
    Generate structured minutes from transcript
    """
    transcript_file = Path(request.transcript_path)
    
    if not transcript_file.exists():
        raise HTTPException(status_code=404, detail="Transcript not found")
    
    # Read transcript
    with open(transcript_file, 'r', encoding='utf-8') as f:
        transcript = f.read()
    
    # Generate summary
    try:
        result = summarizer.generate_minutes(transcript)
        
        # Save summary
        output_dir = Path("data/summaries")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        summary_file = output_dir / f"{transcript_file.stem}_summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(result['summary'])
        
        return {
            "status": "success",
            "summary": result['summary'],
            "saved_to": str(summary_file)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))