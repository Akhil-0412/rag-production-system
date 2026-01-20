import sys
import os
import time

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.retrieval import VectorService
from app.services.embeddings import EmbeddingService
from app.utils.chunking import Chunk

def test_retrieval():
    print("Testing Retrieval (Vector DB)...")
    
    try:
        # 1. Initialize Services
        embed_service = EmbeddingService(provider="local")
        vector_service = VectorService()
        
        # 2. Create Dummy Data
        texts = [
            "Apple is a technology company known for iPhones.",
            "Bananas are a fruit rich in potassium.",
            "The capital of France is Paris."
        ]
        
        # 3. Generate Embeddings
        print("Generating embeddings...")
        embeddings = embed_service.get_embeddings(texts)
        
        # 4. Create Chunk Objects
        chunks = []
        for i, text in enumerate(texts):
            chunks.append(Chunk(
                content=text,
                metadata={"source": "test_script", "chunk_index": i},
                chunk_id=f"test_{i}"
            ))
            
        # 5. Upsert to Pinecone
        print(f"Upserting {len(chunks)} chunks...")
        count = vector_service.upsert_chunks(chunks, embeddings)
        print(f"Upserted {count} vectors.")
        
        # Wait for consistency (Pinecone is eventually consistent)
        print("Waiting 5 seconds for index update...")
        time.sleep(5)
        
        # 6. Query
        query = "What companies make phones?"
        print(f"Querying: '{query}'")
        
        q_embed = embed_service.get_embedding(query)
        results = vector_service.query(q_embed, top_k=2)
        
        print(f"Found {len(results)} results:")
        for res in results:
            print(f" - [{res['score']:.4f}] {res['text']}")
            
        # Check if we retrieved the Apple text
        if any("Apple" in r['text'] for r in results):
            print("\nSUCCESS: Retrieved relevant document.")
        else:
             print("\nFAILURE: Did not retrieve relevant document.")

    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_retrieval()
