from typing import List, Optional
import time
from tenacity import retry, stop_after_attempt, wait_exponential
import os
import warnings

# Suppress HuggingFace warnings
warnings.filterwarnings("ignore", category=FutureWarning)

from app.config import settings

class EmbeddingService:
    def __init__(self, provider: str = None):
        self.provider = provider or settings.EMBEDDING_PROVIDER
        self.client = None
        self.local_model = None
        
        if self.provider == "openai":
            from openai import OpenAI
            if not settings.OPENAI_API_KEY:
                # Fallback to env var if not in settings
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY is not set")
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
            
        elif self.provider == "local":
            print(f"Loading local embedding model: {settings.EMBEDDING_MODEL}...")
            from sentence_transformers import SentenceTransformer
            # Using CPU by default, or CUDA if available
            self.local_model = SentenceTransformer(settings.EMBEDDING_MODEL)
            print("Local model loaded.")
            
        else:
            raise NotImplementedError(f"Provider {self.provider} not supported.")

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_embedding(self, text: str, model: str = None) -> List[float]:
        """
        Get embedding for a single string.
        """
        if not text:
            return []
            
        if self.provider == "openai":
            return self._get_openai_embedding([text], model or settings.EMBEDDING_MODEL)[0]
        elif self.provider == "local":
            return self._get_local_embedding([text])[0]
        return []

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    def get_embeddings(self, texts: List[str], model: str = None) -> List[List[float]]:
        """
        Get embeddings for a list of strings (batch processing).
        """
        if not texts:
            return []
            
        if self.provider == "openai":
             return self._get_openai_embedding(texts, model or settings.EMBEDDING_MODEL)
        elif self.provider == "local":
             return self._get_local_embedding(texts)
        
        return []

    def _get_openai_embedding(self, texts: List[str], model: str) -> List[List[float]]:
        response = self.client.embeddings.create(
            input=texts,
            model=model
        )
        return [item.embedding for item in response.data]

    def _get_local_embedding(self, texts: List[str]) -> List[List[float]]:
        # SentenceTransformers handles batching automatically
        embeddings = self.local_model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()

    def estimate_cost(self, token_count: int, model: str = None) -> float:
        """
        Estimate cost for embedding generation.
        """
        if self.provider == "local":
            return 0.0
            
        model = model or settings.EMBEDDING_MODEL
        price_per_1k = 0.00002 # Default for text-embedding-3-small
        
        if model == "text-embedding-3-large":
            price_per_1k = 0.00013
        elif model == "ada-002":
             price_per_1k = 0.00010
             
        return (token_count / 1000) * price_per_1k
