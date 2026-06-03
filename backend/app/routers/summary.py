"""
Summary router - returns full Q&A log and insight analysis.
GET /summary/{session_id} - returns complete interview summary with traceability and evaluation
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.summary import SummaryResponse, QAPair
from app.services.session_manager import get_session, get_summary_data, get_qa_records

router = APIRouter()


@router.get("/summary/{session_id}", response_model=SummaryResponse)
async def get_summary(
    session_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    """
    Get the complete interview summary for a session.
    Returns all Q&A pairs along with AI-generated insight analysis,
    traceability data (retrieval queries + contexts), and per-answer evaluations.
    """
    # Validate session exists
    session = await get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    try:
        summary_data = await get_summary_data(db, session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")

    # Build Q&A pairs with traceability and evaluation
    qa_records = summary_data["qa_records"]
    qa_pairs = [
        QAPair(
            question_index=r.question_index,
            question=r.question,
            answer=r.answer,
            retrieval_query=r.retrieval_query,
            retrieved_context=r.retrieved_context,
            score=r.score,
            strengths=r.strengths,
            weaknesses=r.weaknesses,
        )
        for r in qa_records
    ]

    return SummaryResponse(
        session_id=session.id,
        role=session.role,
        skills=session.skills,
        experience_years=session.experience_years,
        difficulty=session.difficulty,
        junior_score=session.junior_score,
        mid_score=session.mid_score,
        senior_score=session.senior_score,
        total_questions=len(qa_pairs),
        qa_pairs=qa_pairs,
        insight=summary_data["insight"],
    )