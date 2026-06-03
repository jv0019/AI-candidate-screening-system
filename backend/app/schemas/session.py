from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class SessionCreate(BaseModel):
    role: str
    resume_text: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: UUID
    role: str
    skills: Optional[str] = None
    experience_years: int
    difficulty: str
    current_question_index: int
    is_finished: bool
    created_at: datetime

    class Config:
        from_attributes = True