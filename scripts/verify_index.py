import sys
import os
import traceback

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.config import settings
from pinecone import Pinecone

def verify_index():
    print(f"Connecting to Pinecone index: {settings.PINECONE_INDEX_NAME}...")
    
    try:
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        index = pc.Index(settings.PINECONE_INDEX_NAME)
        
        # Describe index stats to get dimension
        stats = index.describe_index_stats()
        print(f"Index Stats: {stats}")
        
        # We need to fetch the dimension from the index description, not stats
        # Although stats output sometimes implies it, usually we list indexes to get metadata
        desc = pc.describe_index(settings.PINECONE_INDEX_NAME)
        print(f"Index Description: {desc}")
        
        index_dim = desc.dimension
        print(f"Index Dimension: {index_dim}")
        
        # Check against our config
        # Local model 'all-MiniLM-L6-v2' is 384
        # 'text-embedding-3-small' is 1536
        # User apparently has 1024
        
        my_model = settings.EMBEDDING_MODEL
        expected_dim = 384 # Default for our local model
        if "text-embedding" in my_model:
            expected_dim = 1536
            
        print(f"Local Model '{my_model}' expects dimension: {expected_dim}")
        
        if index_dim != expected_dim:
            print("\n!!! DIMENSION MISMATCH !!!")
            print(f"Index has {index_dim}, but your model produces {expected_dim}.")
            print("They MUST match to work.")
            sys.exit(1)
        else:
            print("\nDimensions match! You are good to go.")

    except Exception as e:
        print(f"Verification failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    verify_index()
