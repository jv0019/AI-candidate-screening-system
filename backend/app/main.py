"""
AI-Powered Role-Based Candidate Screening System
FastAPI Backend Entry Point
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db
from app.services.knowledge_base import knowledge_base
from app.routers import upload, interview, summary


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database and knowledge base on startup."""
    print("Starting up: initializing database and knowledge base...")
    await init_db()
    print("Database tables created.")
    knowledge_base.initialize()
    print("Knowledge base initialized.")
    yield
    print("Shutting down.")


app = FastAPI(
    title="AI Candidate Screener API",
    description="AI-powered role-based candidate screening system with RAG pipeline",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(upload.router)
app.include_router(interview.router)
app.include_router(summary.router)


@app.get("/")
async def root():
    return {
        "message": "AI Candidate Screener API",
        "version": "1.0.0",
        "endpoints": {
            "upload_resume": "POST /upload_resume (multipart: file + role)",
            "submit_answer": "POST /answer/{session_id} (JSON: answer)",
            "get_summary": "GET /summary/{session_id}",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.BACKEND_HOST,
        port=settings.BACKEND_PORT,
        reload=True,
    )