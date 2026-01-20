import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.retrieval import VectorService
from app.config import settings

def setup_vectordb():
    print("Setting up Vector Database...")
    
    if not settings.PINECONE_API_KEY:
        print("ERROR: PINECONE_API_KEY not found in environment.")
        return

    try:
        service = VectorService()
        # Verify dimension matches our embedding model
        # all-MiniLM-L6-v2 -> 384
        # text-embedding-3-small -> 1536
        
        dim = 384 
        if "text-embedding" in settings.EMBEDDING_MODEL:
            dim = 1536
            
        print(f"Ensuring index exists with dimension {dim}...")
        service.ensure_index_exists(dimension=dim)
        
        print("Setup complete.")
        
    except Exception as e:
        print(f"Setup failed: {e}")

if __name__ == "__main__":
    setup_vectordb()
