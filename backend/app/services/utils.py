"""
Utility functions for text processing.
"""
import re
import hashlib
from typing import List, Dict, Any, Optional
import json
from datetime import datetime

def detect_tamil(text: str) -> bool:
    tamil_pattern = re.compile(r'[\u0B80-\u0BFF]')
    return bool(tamil_pattern.search(text))

def detect_language(text: str) -> str:
    if detect_tamil(text):
        return 'ta'
    if re.search(r'[a-zA-Z]', text):
        return 'en'
    return 'unknown'

def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    words = re.findall(r'\b\w+\b', text.lower())
    stop_words = {
        'the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i',
        'it', 'for', 'not', 'on', 'with', 'he', 'as', 'you', 'do', 'at',
        'this', 'but', 'his', 'by', 'from', 'they', 'we', 'say', 'her', 'she',
        'or', 'an', 'will', 'my', 'one', 'all', 'would', 'there', 'their'
    }
    words = [w for w in words if w not in stop_words and len(w) > 2]
    if not words:
        return []
    from collections import Counter
    word_counts = Counter(words)
    return [word for word, _ in word_counts.most_common(top_n)]

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,!?;:()\-"]+', ' ', text)
    return text.strip()

def format_transcript(segments: List[Dict[str, Any]]) -> str:
    formatted = []
    current_speaker = None
    current_text = []
    for seg in segments:
        speaker = seg.get('speaker', 'Unknown')
        text = seg.get('text', '')
        if speaker != current_speaker:
            if current_speaker and current_text:
                formatted.append(f"[{current_speaker}]: {' '.join(current_text)}")
            current_speaker = speaker
            current_text = [text]
        else:
            current_text.append(text)
    if current_speaker and current_text:
        formatted.append(f"[{current_speaker}]: {' '.join(current_text)}")
    return '\n\n'.join(formatted)

def extract_definitions(text: str) -> List[Dict[str, str]]:
    definitions = []
    patterns = [
        r'([^.,;]+) (is|are|refers to|means|can be defined as) ([^.]+)\.',
        r'(defined as|known as|called) ([^.]+)',
        r'"([^"]+)" (is|means) ([^.]+)'
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) >= 3:
                definitions.append({
                    'term': match[0].strip(),
                    'definition': match[-1].strip()
                })
    return definitions

def extract_assignments(text: str) -> List[str]:
    assignments = []
    patterns = [
        r'(homework|assignment|project|task|exercise)\s*:?\s*([^.]+)',
        r'please (complete|do|submit|read) ([^.]+)',
        r'(due|deadline) (on|by) ([^.]+)',
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            assignment = ' '.join(match).strip()
            if assignment:
                assignments.append(assignment)
    return assignments

def generate_file_id(filename: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    hash_str = hashlib.md5(f"{filename}{timestamp}".encode()).hexdigest()[:8]
    return f"{timestamp}_{hash_str}"

def safe_filename(filename: str) -> str:
    filename = filename.replace('/', '_').replace('\\', '_')
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return filename