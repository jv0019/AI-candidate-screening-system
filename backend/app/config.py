import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    # Groq (free tier — no payment required, 30 requests/min)
    # Get your key at: https://console.groq.com
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")

    # PostgreSQL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/candidate_screener",
    )

    # Backend Settings
    BACKEND_HOST: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("BACKEND_PORT", "8000"))

    # Chroma Persistent Directory
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")

    # Frontend URL (for CORS)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")

    # Session
    MAX_QUESTIONS_PER_SESSION: int = int(os.getenv("MAX_QUESTIONS_PER_SESSION", "10"))

    # Embeddings use HuggingFace (free/local) — no API key needed
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "knowledge_base")


settings = Settings()