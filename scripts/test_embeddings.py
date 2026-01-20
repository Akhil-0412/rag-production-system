import sys
import os
import time

# Add backend path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.embeddings import EmbeddingService
from app.config import settings

def test_embeddings():
    print("Testing Embedding Service (Local Mode)...")
    
    # Force provider to local for this test if not already set
    provider = settings.EMBEDDING_PROVIDER
    if provider != "local":
        print(f"Warning: Configured provider is {provider}, forcing to 'local' for this test.")
        provider = "local"

    try:
        service = EmbeddingService(provider=provider)
        
        texts = [
            "Hello, world!",
            "This is a test of the RAG system."
        ]
        
        model_name = settings.EMBEDDING_MODEL
        print(f"Generating embeddings for {len(texts)} texts using {model_name}...")
        
        start_time = time.time()
        embeddings = service.get_embeddings(texts)
        duration = time.time() - start_time
        
        print(f"Success! Generated {len(embeddings)} embeddings in {duration:.2f}s")
        print(f"Embedding dimension: {len(embeddings[0])}")
        
        # Check against expected dimension for all-MiniLM-L6-v2 (384)
        if model_name == "all-MiniLM-L6-v2":
            if len(embeddings[0]) == 384:
                print("Dimension Check: PASS (384)")
            else:
                print(f"Dimension Check: WARN (Expected 384, got {len(embeddings[0])})")
             
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_embeddings()
