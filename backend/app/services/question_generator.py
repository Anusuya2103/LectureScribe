# backend/app/services/question_generator.py
from typing import List
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

class HuggingFaceQuestionGenerator:  # Make sure this matches the import
    """Question generator using HuggingFace models."""
    
    def __init__(self, model_name: str = "valhalla/t5-small-qg-hl"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
        self._load_model()
    
    def _load_model(self):
        try:
            print(f"Loading question generation model: {self.model_name}")
            # Load model directly
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)
            
            if torch.cuda.is_available():
                self.model = self.model.to("cuda")
            
            print("Question generation model loaded successfully!")
        except Exception as e:
            print(f"Error loading question generation model: {e}")
            print("Using fallback question generation...")
            self.model = None
            self.tokenizer = None
    
    def generate_questions(self, text: str, num_questions: int = 5) -> List[str]:
        """Generate questions from text."""
        if not self.model or not self.tokenizer:
            return self._fallback_generate(text, num_questions)
        
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text,
                max_length=512,
                truncation=True,
                return_tensors="pt"
            )
            
            if torch.cuda.is_available():
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
            
            # Generate questions
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=64,
                num_beams=min(num_questions, 4),
                num_return_sequences=min(num_questions, 4)
            )
            
            questions = []
            for output in outputs:
                question = self.tokenizer.decode(output, skip_special_tokens=True)
                questions.append(question)
            
            return questions
        except Exception as e:
            print(f"Question generation error: {e}")
            return self._fallback_generate(text, num_questions)
    
    def _fallback_generate(self, text: str, num_questions: int) -> List[str]:
        """Generate simple questions as fallback."""
        sentences = text.split('.')
        questions = []
        for i, sentence in enumerate(sentences[:num_questions]):
            if len(sentence.strip()) > 10:
                questions.append(f"What is the main point of: {sentence[:50]}...?")
        return questions if questions else ["What was discussed in the meeting?"]
    
    def generate_questions_from_lecture(self, transcript_path: str, num_questions: int = 5) -> List[str]:
        """
        Generate questions from a transcript file.
        
        Args:
            transcript_path: Path to transcript file
            num_questions: Number of questions to generate
            
        Returns:
            List of generated questions
        """
        try:
            with open(transcript_path, 'r', encoding='utf-8') as f:
                transcript = f.read()
            return self.generate_questions(transcript, num_questions)
        except Exception as e:
            print(f"Error reading transcript file: {e}")
            return self._fallback_generate("", num_questions)
