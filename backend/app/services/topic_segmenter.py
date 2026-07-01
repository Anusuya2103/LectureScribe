# backend/app/services/topic_segmenter.py
from typing import List, Dict
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import KMeans

class TopicSegmenter:
    """Segment transcript into topics."""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    def segment_topics(self, text: str, segments: List[Dict]) -> List[Dict]:
        """Segment transcript into topics."""
        # Get embeddings for each segment
        texts = [seg.get('text', '') for seg in segments]
        embeddings = self.embedding_model.encode(texts)
        
        # Cluster into topics
        n_topics = min(5, len(texts) // 3)
        if n_topics < 2:
            return [{'topic': 'Main Content', 'segments': segments, 'start': 0, 'end': len(texts)}]
        
        kmeans = KMeans(n_clusters=n_topics, random_state=42)
        labels = kmeans.fit_predict(embeddings)
        
        # Group segments by topic
        topics = []
        for label in set(labels):
            topic_segments = [segments[i] for i in range(len(segments)) if labels[i] == label]
            topic_text = ' '.join([s.get('text', '') for s in topic_segments])
            
            topics.append({
                'topic': self._generate_topic_name(topic_text),
                'segments': topic_segments,
                'start': topic_segments[0].get('start', 0) if topic_segments else 0,
                'end': topic_segments[-1].get('end', 0) if topic_segments else 0
            })
        
        return topics
    
    def _generate_topic_name(self, text: str) -> str:
        """Generate topic name from text."""
        # Extract keywords as topic name
        words = text.split()[:10]
        return ' '.join(words) + '...' if len(words) == 10 else ' '.join(words)