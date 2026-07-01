# backend/app/services/rag_chat.py
import os
import numpy as np
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
from transformers import pipeline

class RAGChatService:
    """RAG-based chat service for transcripts."""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.qa_pipeline = pipeline(
            "question-answering",
            model="distilbert-base-cased-distilled-squad"
        )
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./data/chroma_db"
        ))
        self.collection = None
    
    def index_transcript(self, transcript_id: str, text: str, segments: List[Dict]):
        """Index transcript for RAG."""
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name=f"transcript_{transcript_id}"
        )
        
        # Split into chunks
        chunks = self._chunk_text(text)
        
        # Generate embeddings
        embeddings = self.embedding_model.encode(chunks)
        
        # Store in ChromaDB
        self.collection.add(
            embeddings=embeddings.tolist(),
            documents=chunks,
            ids=[f"{transcript_id}_{i}" for i in range(len(chunks))],
            metadatas=[{"source": transcript_id} for _ in range(len(chunks))]
        )
    
    def chat(self, transcript_id: str, question: str) -> Dict[str, Any]:
        """Chat with transcript using RAG."""
        # Retrieve relevant chunks
        if self.collection is None:
            self.collection = self.chroma_client.get_collection(f"transcript_{transcript_id}")
        
        query_embedding = self.embedding_model.encode([question])
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=3
        )
        
        # Combine context
        context = " ".join(results['documents'][0])
        
        # Generate answer
        answer = self.qa_pipeline(
            question=question,
            context=context
        )
        
        return {
            'question': question,
            'answer': answer['answer'],
            'confidence': answer['score'],
            'sources': results['metadatas'][0]
        }
    
    def _chunk_text(self, text: str, chunk_size: int = 500) -> List[str]:
        """Split text into chunks."""
        words = text.split()
        chunks = []
        for i in range(0, len(words), chunk_size):
            chunk = ' '.join(words[i:i+chunk_size])
            chunks.append(chunk)
        return chunks