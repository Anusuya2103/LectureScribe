# backend/app/services/pipeline.py
from typing import Optional, Dict, Any, List
from pathlib import Path
import os
import json
import re
from datetime import datetime
import librosa
import numpy as np
import tempfile
import soundfile as sf
from deep_translator import GoogleTranslator

from ..config import config
from .transcriber import HuggingFaceTranscriber, TamilTranscriber, EnglishTranscriber
from .summarizer import HuggingFaceSummarizer, StructuredMinutesGenerator
from .diarizer import Diarizer
from .question_generator import HuggingFaceQuestionGenerator
from .audio_processor import AudioProcessor, AudioUtils
from .utils import format_transcript, detect_tamil


class ProcessingPipeline:
    """
    Main processing pipeline orchestrating all services.
    """
    
    def __init__(self):
        # Don't initialize transcribers immediately - lazy loading
        self._transcriber = None
        self._tamil_transcriber = None
        self._english_transcriber = None
        self._summarizer = None
        self._minutes_generator = None
        self._diarizer = None
        self._question_generator = None
        self._audio_processor = None
        self._translator = None
    
    @property
    def translator(self):
        """Lazy load translator."""
        if self._translator is None:
            try:
                self._translator = GoogleTranslator()
                print("✅ Translator loaded successfully!")
            except Exception as e:
                print(f"⚠️ Translator failed to load: {e}")
                self._translator = None
        return self._translator
    
    @property
    def transcriber(self):
        """Lazy load English transcriber (using OpenAI Whisper)."""
        if self._transcriber is None:
            print("Loading English transcriber (base model)...")
            self._transcriber = EnglishTranscriber("base")
        return self._transcriber
    
    @property
    def tamil_transcriber(self):
        """Lazy load Tamil transcriber (using OpenAI Whisper large)."""
        if self._tamil_transcriber is None:
            print("Loading Tamil transcriber (large model)...")
            self._tamil_transcriber = TamilTranscriber("large")
        return self._tamil_transcriber
    
    @property
    def english_transcriber(self):
        """Lazy load English transcriber (using OpenAI Whisper)."""
        if self._english_transcriber is None:
            print("Loading English transcriber (base model)...")
            self._english_transcriber = EnglishTranscriber("base")
        return self._english_transcriber
    
    @property
    def summarizer(self):
        """Lazy load summarizer."""
        if self._summarizer is None:
            print("Loading summarizer...")
            self._summarizer = HuggingFaceSummarizer()
        return self._summarizer
    
    @property
    def minutes_generator(self):
        """Lazy load minutes generator."""
        if self._minutes_generator is None:
            print("Loading minutes generator...")
            self._minutes_generator = StructuredMinutesGenerator(self.summarizer)
        return self._minutes_generator
    
    @property
    def diarizer(self):
        """Lazy load diarizer."""
        if self._diarizer is None:
            print("Loading diarizer...")
            self._diarizer = Diarizer()
        return self._diarizer
    
    @property
    def question_generator(self):
        """Lazy load question generator."""
        if self._question_generator is None:
            print("Loading question generator...")
            self._question_generator = HuggingFaceQuestionGenerator()
        return self._question_generator
    
    @property
    def audio_processor(self):
        """Lazy load audio processor."""
        if self._audio_processor is None:
            self._audio_processor = AudioProcessor()
        return self._audio_processor
    
    def process_full_pipeline(self, audio_path: str, language: str = "auto") -> Dict[str, Any]:
        """
        Run the complete processing pipeline with translation.
        """
        result = {
            'status': 'processing',
            'audio_path': audio_path,
            'transcript': None,
            'transcript_tamil': None,
            'transcript_english': None,
            'bilingual_transcript': None,
            'labeled_transcript': None,
            'summary': None,
            'summary_english': None,
            'summary_tamil': None,
            'structured_minutes': None,
            'questions': None,
            'metadata': {},
            'detected_language': 'unknown'
        }
        
        try:
            # Step 1: Get audio info
            result['metadata'] = AudioUtils.get_audio_info(audio_path)
            
            # Step 2: Transcribe based on language
            print("Step 1: Transcribing...")
            print(f"Language requested: {language}")
            
            # Determine which transcriber to use
            if language == "ta":
                print("🔊 Using Tamil transcriber (large model)...")
                transcribe_result = self.tamil_transcriber.transcribe_tamil(audio_path)
                detected_lang = 'ta'
            elif language == "en":
                print("🔊 Using English transcriber (base model)...")
                transcribe_result = self.english_transcriber.transcribe_english(audio_path)
                detected_lang = 'en'
            else:  # auto
                detected_lang = self._detect_language(audio_path)
                if detected_lang == 'ta':
                    print("🔊 Using Tamil transcriber (large model)...")
                    transcribe_result = self.tamil_transcriber.transcribe_tamil(audio_path)
                else:
                    print("🔊 Using English transcriber (base model)...")
                    transcribe_result = self.english_transcriber.transcribe_english(audio_path)
            
            # Store original transcript
            original_text = transcribe_result['text']
            result['transcript'] = original_text
            
            # Get segments
            segments = transcribe_result.get('segments', [])
            result['segments'] = segments
            
            # If Tamil, translate to English for better processing
            if detected_lang == 'ta':
                print("🌐 Translating Tamil to English for better processing...")
                # Translate the full transcript
                english_text = self._translate_text(original_text)
                result['transcript_tamil'] = original_text
                result['transcript_english'] = english_text
                # Use English for processing
                text_for_processing = english_text
            else:
                result['transcript_english'] = original_text
                text_for_processing = original_text
            
            print(f"Transcription result (first 200 chars): {original_text[:200]}...")
            
            # Save transcript (bilingual if Tamil)
            if detected_lang == 'ta' and result.get('transcript_english'):
                bilingual_text = self._generate_bilingual_transcript(
                    original_text, result['transcript_english']
                )
                result['bilingual_transcript'] = bilingual_text
                transcript_path = self._save_transcript(bilingual_text, audio_path)
            else:
                transcript_path = self._save_transcript(original_text, audio_path)
            
            result['transcript_path'] = transcript_path
            result['saved_to'] = transcript_path
            
            # Step 3: Speaker diarization
            print("Step 2: Speaker diarization...")
            diarization = self.diarizer.diarize(audio_path)
            
            # Step 4: Generate summary (using English for better quality)
            print("Step 3: Generating summary...")
            summary = self.summarizer.summarize(text_for_processing)
            result['summary'] = summary
            result['summary_english'] = summary
            
            # Translate summary back to Tamil if original was Tamil
            if detected_lang == 'ta':
                try:
                    result['summary_tamil'] = self._translate_text(summary, target='ta')
                except:
                    result['summary_tamil'] = summary
            
            # Step 5: Generate structured minutes
            print("Step 4: Generating structured minutes...")
            minutes = self.minutes_generator.generate(text_for_processing)
            result['structured_minutes'] = minutes
            
            # Step 6: Generate questions
            print("Step 5: Generating questions...")
            questions = self.question_generator.generate_questions(
                text_for_processing, num_questions=5
            )
            result['questions'] = questions
            
            result['status'] = 'completed'
            result['detected_language'] = detected_lang
            
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            print(f"Pipeline error: {e}")
        
        return result
    
    def _detect_language(self, audio_path: str) -> str:
        """
        Detect language from audio by checking filename and audio content.
        Returns: 'ta' for Tamil, 'en' for English.
        """
        # First check filename
        if self._detect_tamil_from_filename(audio_path):
            print("🔍 Detected Tamil from filename")
            return 'ta'
        
        # Then analyze audio content
        try:
            print("🔍 Analyzing audio content for language detection...")
            detected = self._detect_language_from_audio(audio_path)
            if detected:
                return detected
        except Exception as e:
            print(f"⚠️ Audio language detection failed: {e}")
        
        # Default to English
        print("🔍 Defaulting to English")
        return 'en'
    
    def _detect_tamil_from_filename(self, audio_path: str) -> bool:
        """
        Detect Tamil from filename.
        
        Checks for:
        1. Tamil Unicode characters (U+0B80 to U+0BFF)
        2. Common Tamil words
        3. Tamil indicators
        """
        filename = os.path.basename(audio_path)
        filename_lower = filename.lower()
        
        print(f"🔍 Checking filename for Tamil: {filename}")
        
        # Check for Tamil Unicode characters (U+0B80 to U+0BFF)
        tamil_pattern = re.compile(r'[\u0B80-\u0BFF]')
        if tamil_pattern.search(filename):
            print(f"✅ Found Tamil Unicode characters in filename")
            return True
        
        # Check for explicit Tamil indicators
        tamil_indicators = ['tamil', 'ta_', 'தமிழ்', 'ta-', '_ta_', '-ta-', 'ta.', '.ta']
        for indicator in tamil_indicators:
            if indicator in filename_lower:
                print(f"✅ Found Tamil indicator '{indicator}' in filename")
                return True
        
        # Check for common Tamil words
        tamil_words = ['தானா', 'இவ்வளவு', 'பயங்கர', 'அலர்ஜி', 'differential']
        for word in tamil_words:
            if word in filename_lower:
                print(f"✅ Found Tamil word '{word}' in filename")
                return True
        
        print(f"❌ No Tamil detected in filename")
        return False
    
    def _detect_language_from_audio(self, audio_path: str) -> str:
        """
        Detect language from audio content by analyzing a sample.
        Returns: 'ta' for Tamil, 'en' for English, or None if uncertain.
        """
        try:
            print("🔍 Sampling audio for language detection...")
            
            # Load a sample of the audio (first 30 seconds)
            audio, sr = librosa.load(audio_path, sr=16000, duration=30)
            
            if len(audio) < sr * 2:  # Less than 2 seconds
                print("⚠️ Audio too short for language detection")
                return None
            
            # Save sample to temp file for transcription
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                sf.write(f.name, audio, sr)
                temp_path = f.name
            
            try:
                # Try Tamil transcriber on the sample
                print("🔄 Testing Tamil model on sample...")
                tamil_result = self.tamil_transcriber.transcribe_tamil(temp_path)
                tamil_text = tamil_result.get('text', '')
                tamil_confidence = self._calculate_confidence(tamil_text, 'ta')
                
                # Try English transcriber on the sample
                print("🔄 Testing English model on sample...")
                english_result = self.english_transcriber.transcribe_english(temp_path)
                english_text = english_result.get('text', '')
                english_confidence = self._calculate_confidence(english_text, 'en')
                
                print(f"📊 Tamil confidence: {tamil_confidence:.2f} (text length: {len(tamil_text)})")
                print(f"📊 English confidence: {english_confidence:.2f} (text length: {len(english_text)})")
                
                # Decision logic - PRIORITIZE TAMIL if there are Tamil characters
                tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', tamil_text))
                
                if tamil_chars > 5:
                    print(f"✅ Tamil text contains {tamil_chars} Tamil characters")
                    return 'ta'
                
                # If Tamil confidence is higher
                if tamil_confidence > english_confidence and tamil_confidence > 0.2:
                    print("✅ Tamil has higher confidence")
                    return 'ta'
                
                # If English confidence is higher
                if english_confidence > tamil_confidence and english_confidence > 0.2:
                    print("✅ English has higher confidence")
                    return 'en'
                
                # If both are similar, use the one with more text
                if len(tamil_text) > len(english_text) * 1.2 and len(tamil_text) > 20:
                    print("✅ Tamil has more text content")
                    return 'ta'
                
                print("⚠️ Uncertain language detection, defaulting to English")
                return 'en'
                
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_path)
                except:
                    pass
                    
        except Exception as e:
            print(f"⚠️ Language detection failed: {e}")
            return None
    
    def _calculate_confidence(self, text: str, language: str) -> float:
        """
        Calculate confidence score for a transcription.
        Higher score = more likely the correct language.
        """
        if not text or len(text) < 5:
            return 0.0
        
        score = 0.0
        total_chars = len(text)
        
        if language == 'ta':
            # Check for Tamil characters
            tamil_pattern = re.compile(r'[\u0B80-\u0BFF]')
            tamil_chars = len(tamil_pattern.findall(text))
            
            if total_chars > 0:
                tamil_ratio = tamil_chars / total_chars
                score = tamil_ratio * 0.8
            
            # Bonus for Tamil words
            tamil_words = ['என்ற', 'இது', 'இந்த', 'ஒரு', 'நாம்', 'அவர்', 'என்பது', 'மிகவும்']
            for word in tamil_words:
                if word in text:
                    score += 0.05
                    break
            
            # Penalty for excessive English (more than 60% English characters)
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            if total_chars > 0 and english_chars / total_chars > 0.6:
                score *= 0.5
                
        elif language == 'en':
            # Check for English characters
            english_chars = len(re.findall(r'[a-zA-Z]', text))
            
            if total_chars > 0:
                english_ratio = english_chars / total_chars
                score = english_ratio * 0.8
            
            # Bonus for English words
            english_words = ['the', 'this', 'that', 'with', 'from', 'have', 'will', 'they', 'what', 'when']
            for word in english_words:
                if word in text.lower():
                    score += 0.05
                    break
            
            # Bonus for mathematical terms
            math_terms = ['equation', 'formula', 'variable', 'constant', 'different', 'calculate']
            for term in math_terms:
                if term in text.lower():
                    score += 0.05
                    break
            
            # Penalty for excessive Tamil (more than 60% Tamil characters)
            tamil_chars = len(re.findall(r'[\u0B80-\u0BFF]', text))
            if total_chars > 0 and tamil_chars / total_chars > 0.6:
                score *= 0.5
        
        # Cap score at 1.0
        return min(score, 1.0)
    
    def _translate_text(self, text: str, target: str = 'en') -> str:
        """Translate text using Google Translate."""
        if not text or not text.strip():
            return text
        
        try:
            if self.translator is None:
                print("⚠️ Translator not available")
                return text
            
            translated = self.translator.translate(text, dest=target)
            return translated
        except Exception as e:
            print(f"Translation error: {e}")
            return text
    
    def _generate_bilingual_transcript(self, tamil_text: str, english_text: str) -> str:
        """Generate bilingual transcript with both languages."""
        bilingual = []
        
        # Split into paragraphs/sentences
        tamil_sentences = tamil_text.split('. ')
        english_sentences = english_text.split('. ')
        
        # Pair them up
        for i in range(max(len(tamil_sentences), len(english_sentences))):
            tamil_part = tamil_sentences[i] + '.' if i < len(tamil_sentences) else ''
            english_part = english_sentences[i] + '.' if i < len(english_sentences) else ''
            if tamil_part or english_part:
                bilingual.append(f"[Tamil] {tamil_part}")
                bilingual.append(f"[English] {english_part}")
        
        return '\n'.join(bilingual)
    
    def _detect_tamil_from_audio(self, audio_path: str) -> bool:
        """
        Detect if audio contains Tamil speech.
        """
        try:
            # Try to use Tamil transcriber if available
            if self._tamil_transcriber is not None:
                tamil_result = self.tamil_transcriber.transcribe_tamil(audio_path)
                text = tamil_result.get('text', '')
                from .utils import detect_tamil
                return detect_tamil(text)
        except Exception as e:
            print(f"Tamil detection failed: {e}")
        
        # Default to False (English) if detection fails
        return False
    
    def _save_transcript(self, transcript: str, audio_path: str) -> str:
        """
        Save transcript to file.
        """
        audio_name = Path(audio_path).stem
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{audio_name}_{timestamp}.txt"
        output_path = config.transcript_dir / filename
        
        # Ensure directory exists
        os.makedirs(config.transcript_dir, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(transcript)
        
        return str(output_path)
    
    def process_only_transcription(self, audio_path: str, language: str = "auto") -> Dict[str, Any]:
        """
        Run only transcription.
        """
        if language == 'ta':
            result = self.tamil_transcriber.transcribe_tamil(audio_path)
        elif language == 'en':
            result = self.english_transcriber.transcribe_english(audio_path)
        else:  # auto
            detected_lang = self._detect_language(audio_path)
            if detected_lang == 'ta':
                result = self.tamil_transcriber.transcribe_tamil(audio_path)
            else:
                result = self.english_transcriber.transcribe_english(audio_path)
        
        # Save transcript
        transcript_path = self._save_transcript(result['text'], audio_path)
        result['saved_to'] = transcript_path
        
        return result
    
    def process_only_summarization(self, transcript_path: str) -> Dict[str, Any]:
        """
        Run only summarization.
        """
        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript = f.read()
        
        summary = self.summarizer.summarize(transcript)
        minutes = self.minutes_generator.generate(transcript)
        
        # Save summary
        audio_name = Path(transcript_path).stem
        summary_path = config.summary_dir / f"{audio_name}_summary.txt"
        
        # Ensure directory exists
        os.makedirs(config.summary_dir, exist_ok=True)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return {
            'summary': summary,
            'structured_minutes': minutes,
            'saved_to': str(summary_path)
        }
    
    def process_with_status(self, audio_path: str, language: str = "auto") -> Dict[str, Any]:
        """
        Process with progress status updates.
        """
        status = {
            'job_id': self._generate_job_id(),
            'status': 'started',
            'progress': 0,
            'steps': []
        }
        
        try:
            # Step 1: Loading
            status['progress'] = 10
            status['steps'].append({'name': 'loading', 'status': 'completed'})
            
            # Step 2: Transcribe
            status['progress'] = 30
            status['steps'].append({'name': 'transcribing', 'status': 'in_progress'})
            transcript_result = self.process_only_transcription(audio_path, language)
            status['steps'][-1]['status'] = 'completed'
            
            # Step 3: Summarize
            status['progress'] = 60
            status['steps'].append({'name': 'summarizing', 'status': 'in_progress'})
            summary_result = self.process_only_summarization(transcript_result['saved_to'])
            status['steps'][-1]['status'] = 'completed'
            
            # Step 4: Finalize
            status['progress'] = 100
            status['status'] = 'completed'
            status['result'] = {
                **transcript_result,
                **summary_result
            }
            
        except Exception as e:
            status['status'] = 'error'
            status['error'] = str(e)
        
        return status
    
    def _generate_job_id(self) -> str:
        """Generate a unique job ID."""
        import uuid
        return str(uuid.uuid4())[:8]