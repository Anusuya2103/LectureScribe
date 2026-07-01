"""
Database repository for CRUD operations.
"""
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from .models import Lecture, SpeakerSegment, Question, ProcessingJob

class LectureRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, file_id: str, filename: str, file_path: str,
               file_size: int, content_type: str) -> Lecture:
        lecture = Lecture(
            file_id=file_id,
            filename=filename,
            file_path=file_path,
            file_size=file_size,
            content_type=content_type,
            status="uploaded"
        )
        self.db.add(lecture)
        self.db.commit()
        self.db.refresh(lecture)
        return lecture
    
    def get_by_id(self, lecture_id: int) -> Optional[Lecture]:
        return self.db.query(Lecture).filter(Lecture.id == lecture_id).first()
    
    def get_by_file_id(self, file_id: str) -> Optional[Lecture]:
        return self.db.query(Lecture).filter(Lecture.file_id == file_id).first()
    
    def get_all(self, skip: int = 0, limit: int = 100) -> List[Lecture]:
        return self.db.query(Lecture).order_by(
            Lecture.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def update_status(self, lecture_id: int, status: str) -> Optional[Lecture]:
        lecture = self.get_by_id(lecture_id)
        if lecture:
            lecture.status = status
            if status == "completed":
                lecture.processed_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(lecture)
        return lecture
    
    def update_transcript(self, lecture_id: int, transcript: str,
                         language: Optional[str] = None) -> Optional[Lecture]:
        lecture = self.get_by_id(lecture_id)
        if lecture:
            lecture.transcript = transcript
            lecture.language = language
            lecture.status = "transcribed"
            self.db.commit()
            self.db.refresh(lecture)
        return lecture
    
    def update_summary(self, lecture_id: int, summary: str,
                       structured: Optional[Dict] = None) -> Optional[Lecture]:
        lecture = self.get_by_id(lecture_id)
        if lecture:
            lecture.summary = summary
            lecture.structured_summary = structured
            lecture.status = "summarized"
            self.db.commit()
            self.db.refresh(lecture)
        return lecture
    
    def update_labeled_transcript(self, lecture_id: int,
                                  labeled: str) -> Optional[Lecture]:
        lecture = self.get_by_id(lecture_id)
        if lecture:
            lecture.labeled_transcript = labeled
            self.db.commit()
            self.db.refresh(lecture)
        return lecture
    
    def set_error(self, lecture_id: int, error: str) -> Optional[Lecture]:
        lecture = self.get_by_id(lecture_id)
        if lecture:
            lecture.status = "error"
            lecture.error_message = error
            self.db.commit()
            self.db.refresh(lecture)
        return lecture

class SpeakerSegmentRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_bulk(self, lecture_id: int, segments: List[Dict]) -> List[SpeakerSegment]:
        speaker_segments = []
        for seg in segments:
            speaker_segment = SpeakerSegment(
                lecture_id=lecture_id,
                speaker=seg.get('speaker', 'Unknown'),
                text=seg.get('text', ''),
                start_time=seg.get('start', 0),
                end_time=seg.get('end', 0),
                confidence=seg.get('confidence', 0.5)
            )
            self.db.add(speaker_segment)
            speaker_segments.append(speaker_segment)
        self.db.commit()
        return speaker_segments

class QuestionRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_bulk(self, lecture_id: int, questions: List[Dict]) -> List[Question]:
        question_objs = []
        for q in questions:
            question = Question(
                lecture_id=lecture_id,
                question=q.get('question', ''),
                answer=q.get('answer', ''),
                type=q.get('type', 'short_answer'),
                options=q.get('options'),
                timestamp=q.get('timestamp')
            )
            self.db.add(question)
            question_objs.append(question)
        self.db.commit()
        return question_objs

class JobRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create(self, lecture_id: int, task_type: str) -> ProcessingJob:
        job_id = str(uuid.uuid4())[:8]
        job = ProcessingJob(
            job_id=job_id,
            lecture_id=lecture_id,
            task_type=task_type,
            status="pending"
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job
    
    def get_by_id(self, job_id: str) -> Optional[ProcessingJob]:
        return self.db.query(ProcessingJob).filter(
            ProcessingJob.job_id == job_id
        ).first()
    
    def update_status(self, job_id: str, status: str,
                     progress: Optional[int] = None) -> Optional[ProcessingJob]:
        job = self.get_by_id(job_id)
        if job:
            job.status = status
            if progress is not None:
                job.progress = progress
            self.db.commit()
            self.db.refresh(job)
        return job
    
    def get_by_lecture_id(self, lecture_id: int) -> List[ProcessingJob]:
        return self.db.query(ProcessingJob).filter(
            ProcessingJob.lecture_id == lecture_id
        ).order_by(ProcessingJob.created_at.desc()).all()
    
    def delete(self, job_id: str) -> bool:
        job = self.get_by_id(job_id)
        if job:
            self.db.delete(job)
            self.db.commit()
            return True
        return False