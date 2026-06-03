"""
Interview router - handles answer submission and adaptive question generation.
POST /answer/{session_id} - accepts answer, returns next question or finished flag
"""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.answer import AnswerRequest
from app.services.session_manager import get_session, process_answer

router = APIRouter()


@router.post("/answer/{session_id}")
async def submit_answer(
    session_id: UUID,
    request: AnswerRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit an answer for the current question and get the next question.
    Returns next question or signals that the interview is finished.
    """
    # Validate session exists
    session = await get_session(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    # Check if already finished
    if session.is_finished:
        return {
            "session_id": str(session_id),
            "question_index": session.current_question_index,
            "finished": True,
            "message": "Interview is already completed. View summary at /summary/{session_id}",
        }

    # Validate answer is not empty
    if not request.answer or not request.answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty")

    try:
        next_question, finished = await process_answer(
            db=db,
            session_id=session_id,
            answer=request.answer.strip(),
        )

        response = {
            "session_id": str(session_id),
            "question_index": session.current_question_index,
            "finished": finished,
        }

        if next_question:
            response["next_question"] = next_question

        if finished:
            response["message"] = "Interview completed! View your summary at /summary/{session_id}"

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing answer: {str(e)}")