from typing import List, Dict, Any
import re
from dataclasses import dataclass
try:
    from app.utils.preprocessing import Document
except ImportError:
    # Fallback for when running scripts directly
    from utils.preprocessing import Document

@dataclass
class Chunk:
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    
class ChunkingStrategy:
    def chunk(self, document: Document) -> List[Chunk]:
        raise NotImplementedError

class FixedSizeChunking(ChunkingStrategy):
    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        self.chunk_size = chunk_size
        self.overlap = overlap
        
    def chunk(self, document: Document) -> List[Chunk]:
        text = document.content
        chunks = []
        start = 0
        
        # Simple character-based sliding window
        # In production, you'd likely want token-based splitting (e.g., using tiktoken)
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            
            # Simple unique ID generation
            chunk_id = f"{document.metadata['source']}_{len(chunks)}"
            
            chunk_metadata = document.metadata.copy()
            chunk_metadata["chunk_index"] = len(chunks)
            chunk_metadata["strategy"] = "fixed_size"
            
            chunks.append(Chunk(
                content=chunk_text,
                metadata=chunk_metadata,
                chunk_id=chunk_id
            ))
            
            start += (self.chunk_size - self.overlap)
            
        return chunks

class SentenceChunking(ChunkingStrategy):
    def chunk(self, document: Document) -> List[Chunk]:
        # Simple regex split on sentence terminators
        sentences = re.split(r'(?<=[.!?])\s+', document.content)
        chunks = []
        
        for i, sentence in enumerate(sentences):
            if not sentence.strip():
                continue
                
            chunk_id = f"{document.metadata['source']}_sent_{i}"
            chunk_metadata = document.metadata.copy()
            chunk_metadata["chunk_index"] = i
            chunk_metadata["strategy"] = "sentence"
            
            chunks.append(Chunk(
                content=sentence,
                metadata=chunk_metadata,
                chunk_id=chunk_id
            ))
            
        return chunks

# Factory/Router
def get_chunker(strategy_name: str = "fixed", **kwargs) -> ChunkingStrategy:
    if strategy_name == "sentence":
        return SentenceChunking()
    elif strategy_name == "fixed":
        return FixedSizeChunking(**kwargs)
    else:
        return FixedSizeChunking(**kwargs)
