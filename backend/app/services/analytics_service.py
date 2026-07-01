# backend/app/services/analytics_service.py
from typing import Dict, Any
import json
from datetime import datetime

class AnalyticsService:
    """Generate lecture analytics."""
    
    def generate_analytics(self, transcript: str, segments: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive analytics."""
        return {
            'summary': {
                'total_duration': segments[-1].get('end', 0) if segments else 0,
                'total_words': len(transcript.split()),
                'total_sentences': len(transcript.split('.')),
                'unique_words': len(set(transcript.lower().split()))
            },
            'speaking_stats': self._calculate_speaking_stats(segments),
            'word_frequency': self._calculate_word_frequency(transcript),
            'readability_score': self._calculate_readability(transcript),
            'engagement_metrics': self._calculate_engagement(segments),
            'topic_coverage': self._analyze_topic_coverage(transcript)
        }
    
    def _calculate_speaking_stats(self, segments: List[Dict]) -> Dict:
        """Calculate speaking statistics."""
        if not segments:
            return {}
        
        speaker_durations = {}
        for seg in segments:
            speaker = seg.get('speaker', 'UNKNOWN')
            duration = seg.get('end', 0) - seg.get('start', 0)
            speaker_durations[speaker] = speaker_durations.get(speaker, 0) + duration
        
        return {
            'total_speakers': len(speaker_durations),
            'speaker_durations': speaker_durations,
            'dominant_speaker': max(speaker_durations, key=speaker_durations.get)
        }
    
    def _calculate_word_frequency(self, text: str) -> Dict:
        """Calculate word frequency."""
        words = text.lower().split()
        freq = {}
        for word in words:
            if len(word) > 3:
                freq[word] = freq.get(word, 0) + 1
        
        # Return top 20
        return dict(sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20])
    
    def _calculate_readability(self, text: str) -> Dict:
        """Calculate readability score."""
        words = text.split()
        sentences = text.split('.')
        
        avg_words = len(words) / max(len(sentences), 1)
        
        # Simple Flesch score approximation
        score = 206.835 - 1.015 * avg_words - 84.6 * (len(text) / max(len(sentences), 1))
        
        return {
            'flesch_score': max(0, min(100, score)),
            'avg_words_per_sentence': avg_words,
            'total_words': len(words),
            'total_sentences': len(sentences)
        }
    
    def _calculate_engagement(self, segments: List[Dict]) -> Dict:
        """Calculate engagement metrics."""
        if not segments:
            return {}
        
        # Calculate silence gaps
        gaps = []
        for i in range(1, len(segments)):
            gap = segments[i].get('start', 0) - segments[i-1].get('end', 0)
            if gap > 1:  # More than 1 second gap
                gaps.append(gap)
        
        return {
            'avg_gap': sum(gaps) / max(len(gaps), 1) if gaps else 0,
            'total_gaps': len(gaps),
            'speaking_pace': len(segments) / max(segments[-1].get('end', 1), 1)
        }
    
    def _analyze_topic_coverage(self, text: str) -> List[Dict]:
        """Analyze topic coverage."""
        # Extract key topics
        topics = []
        common_words = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'i', 'it']
        
        words = text.lower().split()
        for word in set(words):
            if len(word) > 4 and word not in common_words:
                topics.append({
                    'topic': word,
                    'frequency': words.count(word),
                    'coverage': (words.count(word) / len(words)) * 100
                })
        
        return sorted(topics, key=lambda x: x['frequency'], reverse=True)[:10]