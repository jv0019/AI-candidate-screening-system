from pydantic import BaseModel
from typing import List, Optional
from uuid import UUID


class QAPair(BaseModel):
    question_index: int
    question: str
    answer: Optional[str] = None

    # Traceability
    retrieval_query: Optional[str] = None
    retrieved_context: Optional[str] = None

    # Evaluation
    score: Optional[int] = None
    strengths: Optional[str] = None
    weaknesses: Optional[str] = None


class SummaryResponse(BaseModel):
    session_id: UUID
    role: str
    skills: Optional[str] = None
    experience_years: int
    difficulty: str

    # Granular difficulty scores
    junior_score: Optional[int] = None
    mid_score: Optional[int] = None
    senior_score: Optional[int] = None

    total_questions: int
    qa_pairs: List[QAPair]
    insight: Optional[str] = None