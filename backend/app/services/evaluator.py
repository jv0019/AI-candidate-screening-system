"""
Answer evaluation service.
Uses Groq (free tier, OpenAI-compatible API) to score and analyse candidate answers.
"""
from typing import Dict, Optional
import json
from openai import AsyncOpenAI

from app.config import settings


async def evaluate_answer(
    question: str,
    answer: str,
    context_chunks: Optional[list] = None,
) -> Dict:
    """
    Evaluate a candidate's interview answer using Groq.

    Args:
        question: The question that was asked.
        answer: The candidate's answer.
        context_chunks: Relevant knowledge base chunks used for question generation.

    Returns:
        Dict with:
            - score (int): 1–10 rating.
            - strengths (str): bullet list of strengths.
            - weaknesses (str): bullet list of weaknesses.
    """
    if not settings.GROQ_API_KEY:
        return {
            "score": 5,
            "strengths": "Evaluation unavailable (no API key).",
            "weaknesses": "Evaluation unavailable (no API key).",
        }

    reference_context = ""
    if context_chunks:
        reference_context = "\n---\n".join([c for c in context_chunks if c][:3])

    system_prompt = (
        "You are an expert technical interviewer. Evaluate the candidate's answer "
        "to the interview question provided. Be fair, objective, and specific.\n\n"
        "Return your evaluation in the following strict JSON format:\n"
        '{\n  "score": <int 1-10>,\n'
        '  "strengths": "<bullet list of strengths>",\n'
        '  "weaknesses": "<bullet list of weaknesses>"\n}'
    )

    user_prompt = f"""
Question:
{question}

Candidate's Answer:
{answer}
"""
    if reference_context:
        user_prompt += f"\nReference context (for comparison):\n{reference_context[:1500]}"

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
            max_tokens=400,
        )
        content = response.choices[0].message.content.strip()

        # Strip markdown code fences if present
        if content.startswith("```"):
            lines = content.split("\n")
            content = "\n".join(lines[1:-1])

        result = json.loads(content)
        return {
            "score": max(1, min(10, result.get("score", 5))),
            "strengths": result.get("strengths", "Evaluation unavailable.") if isinstance(result.get("strengths"), str) else "\n".join(result.get("strengths", [])),
            "weaknesses": result.get("weaknesses", "Evaluation unavailable.") if isinstance(result.get("weaknesses"), str) else "\n".join(result.get("weaknesses", [])),
        }
    except Exception as e:
        print(f"Error evaluating answer: {e}")
        return {
            "score": 5,
            "strengths": "Evaluation could not be generated.",
            "weaknesses": "Evaluation could not be generated.",
        }