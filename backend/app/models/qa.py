import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base


class QARecord(Base):
    __tablename__ = "qa_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    question_index = Column(Integer, nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)

    # --- Question Traceability ---
    retrieval_query = Column(Text, nullable=True)       # the query used to search Chroma
    retrieved_context = Column(Text, nullable=True)     # the top chunks retrieved

    # --- Answer Evaluation ---
    score = Column(Integer, nullable=True)              # 1–10
    strengths = Column(Text, nullable=True)             # comma-separated or bullet list
    weaknesses = Column(Text, nullable=True)            # comma-separated or bullet list

    created_at = Column(DateTime, default=datetime.utcnow)