from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import query, documents, metrics

app = FastAPI(
    title="RAG Production System API",
    description="API for Retrieval Augmented Generation System",
    version="1.0.0"
)

# CORS Configuration
origins = [
    "http://localhost:5173", # Vite default
    "http://localhost:3000", # React default
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow all for dev convenience, restrict in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(query.router, prefix="/api", tags=["Query"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])

@app.get("/")
def read_root():
    return {"status": "ok", "message": "RAG Backend is running."}
