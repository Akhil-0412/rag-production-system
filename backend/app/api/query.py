from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict
import time

from app.services.embeddings import EmbeddingService
from app.services.retrieval import VectorService
from app.services.generation import GenerationService
from app.services.caching import CacheService
from app.services.routing import Router as QueryRouter
from app.services.monitoring import MonitoringService

router = APIRouter()

# Initialize Services
# Note: Ideally these are dependencies injected, but for simplicity here we instantiate.
embed_service = EmbeddingService(provider="local")
vector_service = VectorService()
# Lazy load generation service to avoid startup errors if keys missing (handled in service)
try:
    gen_service = GenerationService()
except:
    gen_service = None # Handle gracefully
    
cache_service = CacheService()
query_router = QueryRouter()
monitoring_service = MonitoringService()

class QueryRequest(BaseModel):
    query: str
    chat_history: Optional[List[Dict]] = []

class SourceDocument(BaseModel):
    text: str
    metadata: Dict
    score: float

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceDocument]
    latency_ms: float
    model_used: str

@router.post("/query", response_model=QueryResponse)
async def query_rag(request: QueryRequest):
    start_time = time.time()
    query_text = request.query
    
    # 1. Routing
    route = query_router.route_query(query_text)
    
    if route == "chat":
        # Skip RAG, just chat (simple generation without context)
        # For MVP, let's just use the same generation service but with empty context
        # Or a specific "chat" method.
        # We will treat it as RAG with empty context for now or specific prompt.
        
        # Check Cache first even for chat
        cached = cache_service.get_cached_response(query_text)
        if cached:
            latency = (time.time() - start_time) * 1000
            monitoring_service.log_request(query_text, cached['answer'], latency, model="cache", retrieval_count=0)
            return QueryResponse(
                answer=cached['answer'],
                sources=[],
                latency_ms=latency,
                model_used="cache-hit"
            )

        context_chunks = []
        if gen_service:
            answer = gen_service.generate_response(query_text, []) # No context
        else:
            answer = "LLM Service not available."
            
        latency = (time.time() - start_time) * 1000
        monitoring_service.log_request(query_text, answer, latency, model="groq-chat")
        
        # Cache result
        cache_service.set_cached_response(query_text, {"answer": answer})
        
        return QueryResponse(
            answer=answer,
            sources=[],
            latency_ms=latency,
            model_used="groq-chat"
        )
        
    # 2. RAG Flow
    
    # Check Cache
    cached = cache_service.get_cached_response(query_text)
    if cached:
        latency = (time.time() - start_time) * 1000
        monitoring_service.log_request(query_text, cached['answer'], latency, model="cache", retrieval_count=0)
        return QueryResponse(
            answer=cached['answer'],
            sources=cached.get('sources', []),
            latency_ms=latency,
            model_used="cache-hit"
        )

    try:
        # Embed
        query_emb = embed_service.get_embedding(query_text)
        
        # Retrieve
        results = vector_service.query(query_emb, top_k=5)
        
        # Format sources for response
        sources = []
        context_chunks = []
        for res in results:
            src = SourceDocument(text=res['text'], metadata=res['metadata'], score=res['score'])
            sources.append(src)
            context_chunks.append({"text": res['text'], "metadata": res['metadata']})
            
        # Generate
        if gen_service:
            answer = gen_service.generate_response(query_text, context_chunks)
        else:
            answer = "LLM Service not initialized. Check API Keys."
            
        latency = (time.time() - start_time) * 1000
        
        # Log
        monitoring_service.log_request(
            query_text, 
            answer, 
            latency, 
            model="groq-rag", 
            retrieval_count=len(results)
        )
        
        # Cache
        cache_service.set_cached_response(query_text, {
            "answer": answer,
            "sources": [s.dict() for s in sources]
        })
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            latency_ms=latency,
            model_used="groq-rag"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
