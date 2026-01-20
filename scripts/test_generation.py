import sys
import os

# Add backend to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.services.generation import GenerationService
from app.config import settings

def test_generation():
    print("Testing Generation Service (Groq)...")
    
    # Mock context
    mock_context = [
        {"text": "The Python programming language was created by Guido van Rossum and released in 1991.", "metadata": {}},
        {"text": "Python emphasizes code readability with its notable use of significant indentation.", "metadata": {}}
    ]
    
    query = "Who created Python?"
    
    print(f"Query: {query}")
    print(f"Context: {len(mock_context)} chunks provided.")
    
    try:
        service = GenerationService()
        print("Service initialized.")
        
        print("Generating response...")
        response = service.generate_response(query, mock_context)
        
        print("\n--- RESPONSE ---")
        print(response)
        print("----------------")
        
        if "Guido" in response:
            print("\nSUCCESS: Correct answer generated.")
        else:
            print("\nFAILURE: Answer seems incorrect.")
            
    except Exception as e:
        print(f"\nTEST FAILED: {e}")

if __name__ == "__main__":
    test_generation()
