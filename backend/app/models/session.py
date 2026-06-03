import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class Session(Base):
    __tablename__ = "sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    role = Column(String(100), nullable=False)
    resume_text = Column(Text, nullable=True)
    skills = Column(Text, nullable=True)  # comma-separated
    experience_years = Column(Integer, default=0)
    difficulty = Column(String(20), default="medium")  # easy, medium, hard (overall)

    # --- Resume-Aware Difficulty (granular scores) ---
    junior_score = Column(Integer, default=0)   # 0–10 – fundamental concept familiarity
    mid_score = Column(Integer, default=0)      # 0–10 – practical implementation experience
    senior_score = Column(Integer, default=0)   # 0–10 – architecture/design/optimisation depth

    current_question_index = Column(Integer, default=0)
    is_finished = Column(Integer, default=0)  # boolean 0/1
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)