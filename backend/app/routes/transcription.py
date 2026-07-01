from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from ..services.transcriber import WhisperTranscriber

router = APIRouter()
transcriber = WhisperTranscriber("base")  # Start with base model

class TranscribeRequest(BaseModel):
    file_path: str
    language: str = "en"  # en for English, ta for Tamil

@router.post("/transcribe")
async def transcribe_audio(request: TranscribeRequest):
    """
    Transcribe uploaded audio file
    """
    audio_path = Path(request.file_path)
    
    if not audio_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        # Transcribe
        result = transcriber.transcribe_audio(str(audio_path), request.language)
        
        # Save transcript
        output_dir = Path("data/transcripts")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        transcript_file = output_dir / f"{audio_path.stem}.txt"
        with open(transcript_file, 'w', encoding='utf-8') as f:
            f.write(result['text'])
        
        return {
            "status": "success",
            "transcript": result['text'],
            "segments": result.get('segments', []),
            "saved_to": str(transcript_file)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))