import requests
import os
import time

BASE_URL = "http://localhost:8000/api"
FILE_PATH = os.path.join("data", "sample_docs", "2503.00223v3.pdf")

def verify_upload():
    if not os.path.exists(FILE_PATH):
        print(f"File not found: {FILE_PATH}")
        return

    print(f"Uploading {FILE_PATH}...")
    try:
        with open(FILE_PATH, "rb") as f:
            files = {"file": (os.path.basename(FILE_PATH), f, "application/pdf")}
            response = requests.post(f"{BASE_URL}/documents/upload", files=files)
            
        print(f"Upload Status: {response.status_code}")
        if response.status_code == 200:
            print("Upload Response:", response.json())
            return True
        else:
            print("Upload Failed:", response.text)
            return False
    except Exception as e:
        print(f"Upload Error: {e}")
        return False

def verify_query():
    # Wait a bit for indexing (though upsert is usually fast)
    time.sleep(2)
    
    query = "What is the main topic of the uploaded document?"
    print(f"\nQuerying: '{query}'")
    
    try:
        response = requests.post(f"{BASE_URL}/query", json={"query": query})
        data = response.json()
        
        print(f"Query Status: {response.status_code}")
        if response.status_code == 200:
            print("\n--- Answer ---")
            print(data.get("answer"))
            print("--------------")
            
            # Check sources
            sources = data.get("sources", [])
            print(f"\nSources retrieved: {len(sources)}")
            for src in sources:
                # Print metadata to confirm it came from our file
                print(f" - Score: {src.get('score'):.4f}, Source: {src.get('metadata', {}).get('source')}")
        else:
            print("Query Failed:", response.text)
            
    except Exception as e:
        print(f"Query Error: {e}")

if __name__ == "__main__":
    if verify_upload():
        verify_query()
