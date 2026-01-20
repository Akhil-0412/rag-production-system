from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Dict
import os
import shutil
import tempfile

from app.utils.preprocessing import FileLoader
from app.utils.chunking import ChunkingStrategy, get_chunker
from app.services.embeddings import EmbeddingService
from app.services.retrieval import VectorService

router = APIRouter()

# Services
# (In prod, use dependency injection)
embed_service = EmbeddingService(provider="local")
vector_service = VectorService()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a file, process it, and index it into Vector DB.
    """
    allowed_extensions = {".pdf", ".docx", ".txt", ".md"}
    ext = os.path.splitext(file.filename)[1].lower()
    
    if ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type. Allowed: {allowed_extensions}")
    
    try:
        # Save to temp file
        with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
            shutil.copyfileobj(file.file, tmp)
            tmp_path = tmp.name
            
        # Process
        loader = FileLoader()
        chunks = []
        
        # Load content
        # Note: FileLoader typically takes a directory or file path.
        # We need to adapt it or manually use the specific loader method logic
        # For simplicity, let's instantiate FileLoader and use `load_file` if we had it exposed publicly
        # Checking FileLoader implementation... it has `load_directory`. 
        # Let's verify `FileLoader` logic. It uses `_load_pdf`, etc. based on file.
        # We can implement a helper or modify FileLoader to load a single file path publically.
        # Assuming FileLoader defaults to directory but we can use its internal methods or we can just point it to the temp file?
        # Actually FileLoader.load_directory iterates.
        # Let's implement a quick single file load here re-using logic or adding to FileLoader.
        # Better: Add `load_file` to `FileLoader` in `preprocessing.py`.
        # For now, let's rely on `_load_pdf` etc being accessible or copy logic?
        # Accessing protected members is bad practice.
        # Let's update `FileLoader` in a separate step or just do a quick dirty check.
        # Actually FileLoader has `load_documents` which takes a directory. 
        # I will hack specific loader here for API simplicity or assume I can create a temp directory.
        
        # Temp directory approach (re-uses existing robust logic)
        with tempfile.TemporaryDirectory() as temp_dir:
            # Move temp file to temp dir with original name
            final_path = os.path.join(temp_dir, file.filename)
            shutil.move(tmp_path, final_path)
            
            docs = loader.load_directory(temp_dir)
            
        if not docs:
            raise HTTPException(status_code=400, detail="Could not extract text from file.")
            
        # Chunk
        chunker = get_chunker(strategy_name="fixed") # Default
        all_chunks = []
        for doc in docs:
            doc_chunks = chunker.chunk(doc)
            all_chunks.extend(doc_chunks)
            
        # Embed
        texts = [c.content for c in all_chunks]
        embeddings = embed_service.get_embeddings(texts)
        
        # Upsert
        count = vector_service.upsert_chunks(all_chunks, embeddings)
        
        return {
            "filename": file.filename,
            "chunks_created": len(all_chunks),
            "vectors_upserted": count,
            "status": "success"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'tmp_path' in locals() and os.path.exists(tmp_path):
            os.remove(tmp_path)

@router.delete("/reset")
async def reset_index():
    """Delete all vectors."""
    try:
        vector_service.delete_all()
        return {"status": "success", "message": "Index cleared."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
