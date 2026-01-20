import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_root():
    print("Testing Root Endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/")
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        if res.status_code == 200:
            print("SUCCESS")
        else:
            print("FAILURE")
    except Exception as e:
        print(f"Error: {e}")

def test_query():
    print("\nTesting Query Endpoint (Chat/Greeting)...")
    try:
        payload = {"query": "Hello!"}
        res = requests.post(f"{BASE_URL}/api/query", json=payload)
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()}")
        if res.status_code == 200 and "answer" in res.json():
            print("SUCCESS")
        else:
            print("FAILURE")
            
        print("\nTesting Query Endpoint (RAG)...")
        payload = {"query": "What is Python?"}
        res = requests.post(f"{BASE_URL}/api/query", json=payload)
        print(f"Status: {res.status_code}")
        # Truncate for display
        data = res.json()
        if "answer" in data:
            data["answer"] = data["answer"][:100] + "..."
        print(f"Response: {data}")
        
        if res.status_code == 200:
            print("SUCCESS")
        else:
            print("FAILURE")

    except Exception as e:
        print(f"Error: {e}")

def test_metrics():
    print("\nTesting Metrics Endpoint...")
    try:
        res = requests.get(f"{BASE_URL}/api/metrics/recent")
        print(f"Status: {res.status_code}")
        print(f"Response: {res.json()[:2]}") # Show first 2
        if res.status_code == 200:
            print("SUCCESS")
        else:
            print("FAILURE")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Wait for server to be ready
    print("Waiting for server...")
    time.sleep(5)
    test_root()
    test_query()
    test_metrics()
