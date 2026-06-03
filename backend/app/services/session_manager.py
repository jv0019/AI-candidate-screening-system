"""
Session management service.
Orchestrates the interview flow: create session, store Q&A, check completion, generate summary.
Now supports traceability (retrieval_query + retrieved_context), answer evaluation, and granular difficulty scores.
"""
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.session import Session
from app.models.qa import QARecord
from app.config import settings
from app.services.question_generator import generate_first_question, generate_next_question, generate_summary_insight
from app.services.evaluator import evaluate_answer


async def create_session(
    db: AsyncSession,
    role: str,
    resume_text: str,
    skills: List[str],
    experience_years: int,
    difficulty: str,
    junior_score: int = 0,
    mid_score: int = 0,
    senior_score: int = 0,
) -> Session:
    """Create a new interview session in the database."""
    session = Session(
        role=role,
        resume_text=resume_text,
        skills=", ".join(skills),
        experience_years=experience_years,
        difficulty=difficulty,
        junior_score=junior_score,
        mid_score=mid_score,
        senior_score=senior_score,
        current_question_index=0,
        is_finished=0,
    )
    db.add(session)
    await db.flush()
    await db.refresh(session)
    return session


async def save_qa(
    db: AsyncSession,
    session_id: UUID,
    question_index: int,
    question: str,
    answer: Optional[str] = None,
    retrieval_query: Optional[str] = None,
    retrieved_context: Optional[str] = None,
    score: Optional[int] = None,
    strengths: Optional[str] = None,
    weaknesses: Optional[str] = None,
) -> QARecord:
    """Save a Q&A record to the database with traceability and evaluation data."""
    qa = QARecord(
        session_id=session_id,
        question_index=question_index,
        question=question,
        answer=answer,
        retrieval_query=retrieval_query,
        retrieved_context=retrieved_context,
        score=score,
        strengths=strengths,
        weaknesses=weaknesses,
    )
    db.add(qa)
    await db.flush()
    return qa


async def get_session(db: AsyncSession, session_id: UUID) -> Optional[Session]:
    """Get a session by ID."""
    result = await db.execute(select(Session).where(Session.id == session_id))
    return result.scalar_one_or_none()


async def get_qa_records(db: AsyncSession, session_id: UUID) -> List[QARecord]:
    """Get all Q&A records for a session, ordered by index."""
    result = await db.execute(
        select(QARecord)
        .where(QARecord.session_id == session_id)
        .order_by(QARecord.question_index)
    )
    return list(result.scalars().all())


async def get_qa_pairs(db: AsyncSession, session_id: UUID) -> List[Tuple[str, Optional[str]]]:
    """Get Q&A pairs as list of (question, answer) tuples."""
    records = await get_qa_records(db, session_id)
    return [(r.question, r.answer) for r in records]


async def init_first_question(db: AsyncSession, session_id: UUID) -> Tuple[str, str, str]:
    """Generate and save the first question for a session.
    Returns (question, retrieval_query, retrieved_context)."""
    session = await get_session(db, session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    skills_list = session.skills.split(", ") if session.skills else []

    question, retrieval_query, retrieved_context = await generate_first_question(
        role=session.role,
        skills=skills_list,
        difficulty=session.difficulty,
        junior_score=session.junior_score,
        mid_score=session.mid_score,
        senior_score=session.senior_score,
        experience_years=session.experience_years,
    )

    await save_qa(
        db=db,
        session_id=session_id,
        question_index=0,
        question=question,
        retrieval_query=retrieval_query,
        retrieved_context=retrieved_context,
    )

    session.current_question_index = 0
    await db.flush()

    return question, retrieval_query, retrieved_context


async def process_answer(
    db: AsyncSession,
    session_id: UUID,
    answer: str,
) -> Tuple[Optional[str], bool]:
    """
    Process an answer and generate the next question.
    Evaluates the answer and stores score/strengths/weaknesses.
    Returns: (next_question_or_none, is_finished)
    """
    session = await get_session(db, session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    current_idx = session.current_question_index

    # Get the current Q&A record
    result = await db.execute(
        select(QARecord)
        .where(QARecord.session_id == session_id)
        .where(QARecord.question_index == current_idx)
    )
    qa_record = result.scalar_one_or_none()
    if qa_record:
        qa_record.answer = answer

        # Evaluate the answer against the question + retrieved context
        try:
            evaluation = await evaluate_answer(
                question=qa_record.question,
                answer=answer,
                context_chunks=[qa_record.retrieved_context] if qa_record.retrieved_context else None,
            )
            qa_record.score = evaluation["score"]
            qa_record.strengths = evaluation["strengths"]
            qa_record.weaknesses = evaluation["weaknesses"]
        except Exception as e:
            print(f"Warning: Answer evaluation failed: {e}")

        await db.flush()

    # Check if we've reached the max questions
    next_idx = current_idx + 1
    if next_idx >= settings.MAX_QUESTIONS_PER_SESSION:
        session.is_finished = 1
        session.current_question_index = current_idx
        await db.flush()
        return None, True

    # Generate the next question
    previous_qa = await get_qa_pairs(db, session_id)
    skills_list = session.skills.split(", ") if session.skills else []

    next_question, retrieval_query, retrieved_context = await generate_next_question(
        role=session.role,
        skills=skills_list,
        difficulty=session.difficulty,
        previous_qa=previous_qa,
        junior_score=session.junior_score,
        mid_score=session.mid_score,
        senior_score=session.senior_score,
        experience_years=session.experience_years,
    )

    # Save the next question with traceability
    await save_qa(
        db=db,
        session_id=session_id,
        question_index=next_idx,
        question=next_question,
        retrieval_query=retrieval_query,
        retrieved_context=retrieved_context,
    )

    session.current_question_index = next_idx
    await db.flush()

    return next_question, False


async def get_summary_data(db: AsyncSession, session_id: UUID) -> dict:
    """
    Get full summary data for a session including Q&A and generated insight.
    """
    session = await get_session(db, session_id)
    if not session:
        raise ValueError(f"Session {session_id} not found")

    qa_records = await get_qa_records(db, session_id)
    qa_pairs = [(r.question, r.answer) for r in qa_records]

    insight = await generate_summary_insight(
        role=session.role,
        skills=session.skills.split(", ") if session.skills else [],
        difficulty=session.difficulty,
        qa_pairs=qa_pairs,
    )

    return {
        "session": session,
        "qa_pairs": qa_pairs,
        "qa_records": qa_records,
        "insight": insight,
    }