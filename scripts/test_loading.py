import sys
import os

# Add backend path to sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from app.utils.preprocessing import FileLoader
from app.utils.chunking import get_chunker

def test_loading():
    loader = FileLoader()
    docs_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_docs')
    
    print(f"Loading docs from: {docs_dir}")
    documents = loader.load_directory(docs_dir)
    
    print(f"Successfully loaded {len(documents)} documents.")
    
    chunker = get_chunker("fixed", chunk_size=500, overlap=50)
    
    for doc in documents:
        print(f"\nProcessing: {doc.metadata['source']}")
        print(f"Content length: {len(doc.content)} chars")
        
        chunks = chunker.chunk(doc)
        print(f"Generated {len(chunks)} chunks.")
        if chunks:
            print(f"First chunk preview: {chunks[0].content[:100]}...")

if __name__ == "__main__":
    test_loading()
