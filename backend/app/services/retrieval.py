from typing import List, Dict, Any, Optional
import time
from pinecone import Pinecone, ServerlessSpec
from app.config import settings
from app.utils.chunking import Chunk

class VectorService:
    def __init__(self):
        if not settings.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is not set in configuration.")
            
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        
        # We don't connect to the index immediately in constructor to allow for 
        # index creation scripts to run first, but we can try lazy loading.

    def ensure_index_exists(self, dimension: int = 384, metric: str = "cosine"):
        """
        Check if index exists, create if not. 
        Note: 384 is default for all-MiniLM-L6-v2.
        """
        existing_indexes = [i.name for i in self.pc.list_indexes()]
        
        if self.index_name not in existing_indexes:
            print(f"Creating Pinecone index '{self.index_name}'...")
            try:
                self.pc.create_index(
                    name=self.index_name,
                    dimension=dimension,
                    metric=metric,
                    spec=ServerlessSpec(
                        cloud="aws",
                        region=settings.PINECONE_ENV
                    )
                )
                print(f"Index '{self.index_name}' created successfully.")
            except Exception as e:
                print(f"Error creating index: {e}")
                raise e
        else:
            print(f"Index '{self.index_name}' already exists.")

    def get_index(self):
        if not self.index:
            self.index = self.pc.Index(self.index_name)
        return self.index

    def upsert_chunks(self, chunks: List[Chunk], embeddings: List[List[float]]):
        """
        Upsert chunks and their embeddings to Pinecone.
        """
        index = self.get_index()
        vectors = []
        
        for chunk, embedding in zip(chunks, embeddings):
            # Pinecone expects (id, values, metadata)
            # Metadata values must be strings, numbers, booleans, or list of strings
            
            # Clean metadata to ensure compatibility
            clean_metadata = {
                "text": chunk.content, # Storing text in metadata for retrieval
                "chunk_index": int(chunk.metadata.get("chunk_index", 0)),
                "source": str(chunk.metadata.get("source", "")),
                "page": str(chunk.metadata.get("page", "")) if chunk.metadata.get("page") else ""
            }
            
            vectors.append({
                "id": chunk.chunk_id,
                "values": embedding,
                "metadata": clean_metadata
            })
            
        # Batch upload (Pinecone suggests batches of 100 or so)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i+batch_size]
            index.upsert(vectors=batch)
            
        return len(vectors)

    def query(self, query_embedding: List[float], top_k: int = 5, filter: Optional[Dict] = None) -> List[Dict]:
        """
        Query the vector database.
        """
        index = self.get_index()
        
        result = index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True,
            filter=filter
        )
        
        matches = []
        for match in result.matches:
            matches.append({
                "id": match.id,
                "score": match.score,
                "metadata": match.metadata,
                "text": match.metadata.get("text", "")
            })
            
        return matches

    def delete_all(self):
        index = self.get_index()
        index.delete(delete_all=True)
