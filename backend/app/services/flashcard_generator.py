# backend/app/services/flashcard_generator.py
from typing import List, Dict
import re

class FlashcardGenerator:
    """Generate flashcards and MCQs from transcript."""
    
    def generate_flashcards(self, text: str, num_cards: int = 10) -> List[Dict]:
        """Generate flashcards from transcript."""
        # Extract key sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        flashcards = []
        for i, sentence in enumerate(sentences[:num_cards]):
            # Create Q&A pairs
            flashcards.append({
                'id': i + 1,
                'question': self._generate_question(sentence),
                'answer': sentence,
                'source': f'Segment {i+1}'
            })
        
        return flashcards
    
    def generate_mcq(self, text: str, num_questions: int = 5) -> List[Dict]:
        """Generate multiple choice questions."""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
        
        mcqs = []
        for i, sentence in enumerate(sentences[:num_questions]):
            # Generate MCQs
            mcqs.append({
                'id': i + 1,
                'question': self._generate_question(sentence),
                'options': self._generate_options(sentence),
                'correct_answer': 0,
                'explanation': f"Based on the lecture: {sentence[:100]}..."
            })
        
        return mcqs
    
    def _generate_question(self, sentence: str) -> str:
        """Generate a question from a sentence."""
        # Simple question generation
        if ' is ' in sentence:
            parts = sentence.split(' is ', 1)
            return f"What is {parts[0].strip()}?"
        return f"What is the meaning of: {sentence[:50]}...?"
    
    def _generate_options(self, sentence: str) -> List[str]:
        """Generate options for MCQ."""
        words = sentence.split()
        if len(words) > 5:
            return [
                sentence[:100] + "...",
                "This is a distractor option",
                "Another distractor",
                "One more distractor"
            ]
        return ["Option A", "Option B", "Option C", "Option D"]