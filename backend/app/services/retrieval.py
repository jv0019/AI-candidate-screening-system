"""
Dynamic retrieval service.
Constructs search queries from resume + role + previous Q&A context.
Retrieves chunks that test understanding BEYOND what the resume claims.
"""
from typing import List, Tuple, Optional

from app.services.knowledge_base import knowledge_base


def build_search_query(
    role: str,
    skills: List[str],
    experience_years: int = 0,
    difficulty: str = "medium",
    previous_qa: List[Tuple[str, Optional[str]]] = None,
) -> str:
    """
    Build a targeted retrieval query that goes beyond resume claims.
    
    Constructs a query that asks the knowledge base for material that can
    assess a candidate's depth of understanding, not just factual recall.
    """
    skills_str = ", ".join(skills[:7]) if skills else "general technical skills"

    # Base query that probes depth
    parts = [
        f"Technical concepts related to {role}",
        f"Candidate knows: {skills_str}",
        f"Inferred experience: {experience_years} years at {difficulty} level",
    ]

    # Add adaptive context from previous Q&A
    if previous_qa:
        recent = previous_qa[-2:]
        for q, a in recent:
            if q:
                parts.append(f"Previously asked: {q}")
            if a:
                parts.append(f"Candidate answered: {a[:150]}")

    return (
        f"Assessment context for {role} screening.\n"
        f"Candidate's demonstrated skills: {skills_str}\n"
        f"Inferred experience depth: {experience_years} years ({difficulty} level)\n"
        + ("\n".join(parts[2:]) if len(parts) > 2 else "")
        + "\n\n"
        "Objective: Find knowledge base content that can assess "
        "understanding BEYOND what the resume claims — test depth, "
        f"trade-offs, and practical problem-solving in {role} contexts."
    )


def retrieve_relevant_context(
    role: str,
    skills: List[str],
    experience_years: int = 0,
    difficulty: str = "medium",
    previous_qa: List[Tuple[str, Optional[str]]] = None,
    k: int = 5,
) -> Tuple[List[str], str]:
    """
    Retrieve relevant knowledge base chunks for question generation.
    
    Returns:
        (chunks_list, query_used)
    """
    query = build_search_query(role, skills, experience_years, difficulty, previous_qa)

    if not query.strip():
        return [], query

    chunks = knowledge_base.search(query, k=k)
    return chunks, query