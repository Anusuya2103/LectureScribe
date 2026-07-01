# backend/app/services/parallel_transcriber.py
import os
import whisper
import torch
import librosa
import numpy as np
from typing import List, Dict, Any, Optional
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import concurrent.futures
import tempfile
import soundfile as sf
from pathlib import Path
import time

class ParallelTranscriber:
    """Optimized parallel processing for transcription with reduced system load."""
    
    def __init__(self, model_name: str = "large", num_workers: int = 2):
        """
        Initialize parallel transcriber with optimized settings.
        
        Args:
            model_name: Whisper model size
            num_workers: Number of parallel workers (default: 2 to avoid system hang)
        """
        self.model_name = model_name
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Limit workers to prevent system hang
        max_workers = min(2, os.cpu_count() or 2)  # Use at most 2 workers
        self.num_workers = min(num_workers, max_workers)
        
        print(f"🔧 Using {self.num_workers} workers (limited to prevent system hang)")
        self.model = None
        
        # Load model once
        self._load_model()
    
    def _load_model(self):
        """Load Whisper model."""
        try:
            print(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name, device=self.device)
            print(f"✅ Model loaded on {self.device}!")
        except Exception as e:
            print(f"Error loading model: {e}")
            self.model = None
    
    def transcribe_parallel(self, audio_path: str, language: str = "ta") -> Dict[str, Any]:
        """
        Transcribe audio using optimized parallel processing.
        
        Args:
            audio_path: Path to audio file
            language: Language code
        
        Returns:
            Combined transcription result
        """
        if self.model is None:
            raise RuntimeError("Model not loaded.")
        
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        
        # Load and prepare audio
        print(f"Loading audio: {audio_path}")
        audio, sr = librosa.load(audio_path, sr=16000)
        duration = len(audio) / sr
        
        print(f"Audio duration: {duration:.2f} seconds")
        
        # Determine chunk size - larger chunks for fewer chunks
        chunk_duration = 45  # seconds (increased from 30)
        chunk_samples = int(chunk_duration * sr)
        
        # Split into chunks with smaller overlap
        overlap = 1  # seconds (reduced from 2)
        overlap_samples = int(overlap * sr)
        
        chunks = []
        for start in range(0, len(audio), chunk_samples - overlap_samples):
            end = min(start + chunk_samples, len(audio))
            chunk = audio[start:end]
            if len(chunk) > sr * 3:  # Skip chunks shorter than 3 seconds
                chunks.append({
                    'data': chunk,
                    'start_time': start / sr,
                    'end_time': end / sr
                })
        
        # Limit number of chunks to prevent system hang
        max_chunks = 6  # Maximum chunks to process
        if len(chunks) > max_chunks:
            print(f"⚠️ Too many chunks ({len(chunks)}). Limiting to {max_chunks} chunks.")
            # Merge smaller chunks
            chunks = self._merge_small_chunks(chunks, max_chunks)
        
        print(f"🔄 Processing {len(chunks)} chunks with {self.num_workers} workers")
        
        # Process chunks in parallel
        if self.device == "cuda":
            return self._transcribe_gpu(chunks, language)
        else:
            return self._transcribe_cpu(chunks, language)
    
    def _merge_small_chunks(self, chunks: List[Dict], max_chunks: int) -> List[Dict]:
        """Merge small chunks to reduce total number."""
        if len(chunks) <= max_chunks:
            return chunks
        
        merged = []
        chunk_size = max(1, len(chunks) // max_chunks)
        for i in range(0, len(chunks), chunk_size):
            merged_chunks = chunks[i:i+chunk_size]
            
            # Combine audio data
            combined_data = np.concatenate([c['data'] for c in merged_chunks])
            merged.append({
                'data': combined_data,
                'start_time': merged_chunks[0]['start_time'],
                'end_time': merged_chunks[-1]['end_time']
            })
        
        return merged
    
    def _transcribe_gpu(self, chunks: List[Dict], language: str) -> Dict[str, Any]:
        """Transcribe using GPU with threads."""
        results = []
        
        with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
            futures = []
            for chunk in chunks:
                future = executor.submit(
                    self._transcribe_chunk_gpu,
                    chunk['data'],
                    chunk['start_time'],
                    language
                )
                futures.append(future)
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Chunk processing failed: {e}")
        
        return self._merge_results(results)
    
    def _transcribe_cpu(self, chunks: List[Dict], language: str) -> Dict[str, Any]:
        """Transcribe using CPU with processes."""
        results = []
        
        with ProcessPoolExecutor(max_workers=self.num_workers) as executor:
            tasks = []
            for chunk in chunks:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    sf.write(f.name, chunk['data'], 16000)
                    tasks.append({
                        'file_path': f.name,
                        'start_time': chunk['start_time']
                    })
            
            futures = []
            for task in tasks:
                future = executor.submit(
                    self._transcribe_chunk_cpu,
                    task['file_path'],
                    task['start_time'],
                    language,
                    self.model_name
                )
                futures.append(future)
            
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Chunk processing failed: {e}")
        
        # Clean up temp files
        for task in tasks:
            try:
                os.remove(task['file_path'])
            except:
                pass
        
        return self._merge_results(results)
    
    def _transcribe_chunk_gpu(self, audio_chunk: np.ndarray, start_time: float, 
                             language: str) -> Dict:
        """Transcribe a single chunk on GPU."""
        result = self.model.transcribe(
            audio_chunk,
            language=language,
            task="transcribe",
            temperature=0.0,
            fp16=False,
            condition_on_previous_text=False
        )
        
        return {
            'text': result['text'],
            'segments': result.get('segments', []),
            'start_time': start_time
        }
    
    @staticmethod
    def _transcribe_chunk_cpu(file_path: str, start_time: float, 
                              language: str, model_name: str) -> Dict:
        """Transcribe a single chunk on CPU."""
        model = whisper.load_model(model_name, device="cpu")
        
        result = model.transcribe(
            file_path,
            language=language,
            task="transcribe",
            temperature=0.0,
            fp16=False,
            condition_on_previous_text=False
        )
        
        return {
            'text': result['text'],
            'segments': result.get('segments', []),
            'start_time': start_time
        }
    
    def _merge_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Merge results from all chunks."""
        if not results:
            return {'text': '', 'segments': [], 'language': 'ta', 'duration': 0}
        
        # Sort by start time
        results.sort(key=lambda x: x['start_time'])
        
        # Combine text
        full_text = ' '.join([r['text'] for r in results])
        
        # Combine segments with adjusted timestamps
        all_segments = []
        for r in results:
            start_time = r['start_time']
            for seg in r.get('segments', []):
                all_segments.append({
                    'text': seg.get('text', ''),
                    'start': start_time + seg.get('start', 0),
                    'end': start_time + seg.get('end', 0)
                })
        
        return {
            'text': full_text,
            'segments': all_segments,
            'language': 'ta',
            'duration': results[-1]['start_time'] + 30 if results else 0
        }