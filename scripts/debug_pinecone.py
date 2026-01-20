import sys
import os
import traceback

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.config import settings
from pinecone import Pinecone

def debug_pinecone():
    try:
        print(f"Checking API Key: {'Present' if settings.PINECONE_API_KEY else 'Missing'}")
        print(f"Region: {settings.PINECONE_ENV}")
        
        pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        print("Listing indexes...")
        indexes = pc.list_indexes()
        print(f"Indexes: {indexes}")
        
    except Exception as e:
        print("An error occurred:")
        traceback.print_exc()
        with open("debug_log.txt", "w") as f:
            f.write(str(e))
            f.write("\n")
            traceback.print_exc(file=f)

if __name__ == "__main__":
    debug_pinecone()
