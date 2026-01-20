import sys
import os
import traceback

print("Starting debug script...", flush=True)

try:
    # Add backend to sys.path
    sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
    print("Added backend to path.", flush=True)

    from app.config import settings
    print("Imported settings.", flush=True)

    from pinecone import Pinecone
    print("Imported Pinecone.", flush=True)

    if not settings.PINECONE_API_KEY:
        print("ERROR: PINECONE_API_KEY is None/Empty in settings.", flush=True)
    else:
        # Mask key for security in logs
        masked_key = settings.PINECONE_API_KEY[:4] + "..." + settings.PINECONE_API_KEY[-4:]
        print(f"API Key found: {masked_key}", flush=True)

    print(f"Region: {settings.PINECONE_ENV}", flush=True)
    
    if settings.PINECONE_API_KEY:
        try:
            pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            print("Pinecone client initialized. Listing indexes...", flush=True)
            indexes = pc.list_indexes()
            print(f"Indexes: {indexes}", flush=True)
        except Exception as py_e:
             print(f"Pinecone connection error: {py_e}", flush=True)
             traceback.print_exc()

except Exception as e:
    print("An unexpected error occurred during setup:", flush=True)
    traceback.print_exc()
