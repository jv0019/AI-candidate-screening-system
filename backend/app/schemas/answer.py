from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class AnswerRequest(BaseModel):
    answer: str


class QuestionResponse(BaseModel):
    session_id: UUID
    question_index: int
    question: str
    finished: bool = False


class AnswerResponse(BaseModel):
    session_id: UUID
    question_index: int
    next_question: Optional[str] = None
    finished: bool = False