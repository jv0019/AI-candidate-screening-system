"""
Question generation service using Groq (free tier, OpenAI-compatible API).
Generates non-generic, role-specific questions adapted to the candidate's resume.
Supports traceability (returns query + context) and granular difficulty scores.
"""
from typing import List, Optional, Tuple
from openai import AsyncOpenAI

from app.config import settings
from app.services.retrieval import retrieve_relevant_context


async def generate_question(
    role: str,
    skills: List[str],
    difficulty: str,
    previous_qa: List[Tuple[str, Optional[str]]] = None,
    context_chunks: List[str] = None,
    junior_score: int = 0,
    mid_score: int = 0,
    senior_score: int = 0,
) -> Tuple[str, str, str]:
    """
    Generate a role-specific, adaptive interview question using Groq.
    
    Returns:
        (question_text, retrieval_query_used, retrieved_context_used)
    """
    if not settings.GROQ_API_KEY:
        print("Warning: No Groq API key found. Using fallback question.")
        return _get_fallback_question(role, difficulty), "", ""

    # Build granular difficulty targeting
    granular_prompt = ""
    if any([junior_score, mid_score, senior_score]):
        granular_prompt = (
            f"\nGranular candidate profile (0–10 scale):\n"
            f"- Junior (fundamentals): {junior_score}/10\n"
            f"- Mid (implementation):  {mid_score}/10\n"
            f"- Senior (architecture): {senior_score}/10\n"
            f"Target the question at their {difficulty} level overall, "
            f"but probe the areas where their score is weakest to test depth."
        )

    system_prompt = f"""You are an expert technical interviewer for {role} positions.
Generate ONE focused, non-generic interview question that:
- Is specific to the {role} role
- Tests practical knowledge and problem-solving ability
- Matches the candidate's skill level ({difficulty} difficulty)
- Is NOT a generic question like "tell me about yourself" or "what is your weakness"
{granular_prompt}

Difficulty guidelines:
- easy: Fundamental concepts, basic definitions, simple implementation details
- medium: Intermediate problem-solving, design decisions, trade-offs
- hard: Complex system design, advanced optimization, edge cases, research-level concepts

Output ONLY the question text — no labels, no numbering, no prefixes."""

    retrieval_query = ""
    retrieved_context = ""

    kb_context = ""
    if context_chunks:
        kb_context = "\n\nRelevant reference material:\n" + "\n---\n".join(context_chunks[:3])
        retrieved_context = "\n---\n".join(context_chunks[:3])[:1000]

    qa_context = ""
    if previous_qa:
        qa_lines = []
        for i, (q, a) in enumerate(previous_qa[-3:], 1):
            qa_lines.append(f"Q{i}: {q}")
            if a:
                qa_lines.append(f"A{i}: {a[:200]}")
        if qa_lines:
            qa_context = "\n\nPrevious questions and answers:\n" + "\n".join(qa_lines)

    skills_str = ", ".join(skills) if skills else "general"

    if context_chunks:
        retrieval_query = (
            f"Role: {role} | Skills: {skills_str} | Difficulty: {difficulty} | "
            f"Scores: J={junior_score}/10 M={mid_score}/10 S={senior_score}/10"
        )

    user_prompt = f"""Role: {role}
Candidate's skills: {skills_str}
Difficulty level: {difficulty}
{qa_context}
{kb_context}

Generate a single, focused technical interview question based on the above context."""

    try:
        client = AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
        )
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            max_tokens=300,
        )
        question = response.choices[0].message.content.strip()
        return question, retrieval_query, retrieved_context
    except Exception as e:
        print(f"Error generating question with Groq: {e}")
        return _get_fallback_question(role, difficulty), retrieval_query, retrieved_context


async def generate_summary_insight(
    role: str,
    skills: List[str],
    difficulty: str,
    qa_pairs: List[Tuple[str, Optional[str]]],
) -> str:
    """Generate a summary insight/analysis of the candidate's interview performance using Groq."""
    if not settings.GROQ_API_KEY:
        return "Summary insight generation unavailable (no API key). Please review the Q&A log manually."

    qa_text = "\n".join(
        [f"Q: {q}\nA: {a or '[not answered]'}" for q, a in qa_pairs]
    )

    system_prompt = f"""You are an AI hiring assistant. Analyze the following interview Q&A for a {role} candidate.
Provide a concise insight summary including:
1. Overall assessment of their knowledge depth
2. Key strengths demonstrated
3. Areas that need improvement
4. A recommendation (Strong Hire, Hire, Weak Hire, or No Hire)

Be objective and specific. Reference their answers."""

    user_prompt = f"""Role: {role}
Skills: {', '.join(skills)}
Difficulty: {difficulty}

Interview Q&A:
{qa_text}

Provide your analysis:"""

    try:
        client = AsyncOpenAI(
            api_key=settings.GROQ_API_KEY,
            base_url=settings.GROQ_BASE_URL,
        )
        response = await client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating summary insight: {e}")
        return "Summary insight generation unavailable. Please review the Q&A log manually."


async def generate_first_question(
    role: str,
    skills: List[str],
    difficulty: str,
    junior_score: int = 0,
    mid_score: int = 0,
    senior_score: int = 0,
    experience_years: int = 0,
) -> Tuple[str, str, str]:
    """Generate the first question for a new session."""
    context_chunks, retrieval_query = retrieve_relevant_context(
        role, skills, experience_years, difficulty,
    )
    question, _, retrieved_context = await generate_question(
        role, skills, difficulty,
        previous_qa=None,
        context_chunks=context_chunks,
        junior_score=junior_score,
        mid_score=mid_score,
        senior_score=senior_score,
    )
    return question, retrieval_query, retrieved_context


async def generate_next_question(
    role: str,
    skills: List[str],
    difficulty: str,
    previous_qa: List[Tuple[str, Optional[str]]],
    junior_score: int = 0,
    mid_score: int = 0,
    senior_score: int = 0,
    experience_years: int = 0,
) -> Tuple[str, str, str]:
    """Generate an adaptive follow-up question based on previous Q&A."""
    context_chunks, retrieval_query = retrieve_relevant_context(
        role, skills, experience_years, difficulty, previous_qa,
    )
    question, _, retrieved_context = await generate_question(
        role, skills, difficulty,
        previous_qa=previous_qa,
        context_chunks=context_chunks,
        junior_score=junior_score,
        mid_score=mid_score,
        senior_score=senior_score,
    )
    return question, retrieval_query, retrieved_context


def _get_fallback_question(role: str, difficulty: str) -> str:
    """Return a fallback question if Groq generation fails."""
    fallbacks = {
        "AI/ML Engineer": {
            "easy": "Explain the bias-variance tradeoff in machine learning models.",
            "medium": "How would you design a recommendation system for an e-commerce platform? Discuss the key components and trade-offs.",
            "hard": "Compare and contrast Transformer architectures with RNNs for sequence modeling. When would you choose one over the other?",
        },
        "Backend Engineer": {
            "easy": "What is the difference between SQL and NoSQL databases? When would you use each?",
            "medium": "Design a rate-limiting mechanism for a high-traffic API. What approaches would you consider and what are their trade-offs?",
            "hard": "How would you design a distributed caching system that maintains consistency across multiple data centers? Discuss CAP theorem implications.",
        },
        "Data Scientist": {
            "easy": "What is the difference between supervised and unsupervised learning? Give examples of each.",
            "medium": "You're given a dataset with class imbalance. What techniques would you use to handle it and why?",
            "hard": "Design an A/B testing framework for a recommendation algorithm change. How would you handle novelty effects and ensure statistical validity?",
        },
    }

    role_qs = fallbacks.get(role, fallbacks["AI/ML Engineer"])
    return role_qs.get(difficulty, role_qs["medium"])