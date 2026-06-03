"""
Upload router - handles resume upload and initial question generation.
POST /upload_resume - accepts PDF file + role, returns session_id + first question
"""
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.services.resume_parser import parse_resume
from app.services.session_manager import create_session, init_first_question

router = APIRouter()

UPLOAD_DIR = "/tmp/resumes"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_ROLES = ["AI/ML Engineer", "Backend Engineer", "Data Scientist"]


@router.post("/upload_resume")
async def upload_resume(
    file: UploadFile = File(...),
    role: str = Form(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a resume PDF and specify the target role.
    Returns session_id and the first generated interview question.
    """
    # Validate role
    if role not in ALLOWED_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(ALLOWED_ROLES)}",
        )

    # Validate file type
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are accepted.",
        )

    # Save uploaded file temporarily
    file_id = str(uuid.uuid4())
    temp_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file.filename}")

    try:
        content = await file.read()
        with open(temp_path, "wb") as f:
            f.write(content)

        # Parse resume (now returns 7 values including granular scores)
        try:
            resume_text, skills, experience_years, difficulty, junior_score, mid_score, senior_score = parse_resume(temp_path, role)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Failed to parse resume PDF: {str(e)}",
            )

        # Create session in database with granular scores
        session = await create_session(
            db=db,
            role=role,
            resume_text=resume_text,
            skills=skills,
            experience_years=experience_years,
            difficulty=difficulty,
            junior_score=junior_score,
            mid_score=mid_score,
            senior_score=senior_score,
        )

        # Generate and save first question (now returns traceability data too)
        try:
            first_question, retrieval_query, retrieved_context = await init_first_question(
                db=db, session_id=session.id
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate first question: {str(e)}",
            )

        return {
            "session_id": str(session.id),
            "role": session.role,
            "skills": session.skills,
            "experience_years": session.experience_years,
            "difficulty": session.difficulty,
            "junior_score": session.junior_score,
            "mid_score": session.mid_score,
            "senior_score": session.senior_score,
            "question_index": 0,
            "question": first_question,
            "finished": False,
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass