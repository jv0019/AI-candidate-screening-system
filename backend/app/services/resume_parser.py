"""
Resume parsing service.
Extracts text from PDF, identifies skills, and infers difficulty level
with granular (junior/mid/senior) scores.
"""
import re
import os
from typing import List, Tuple, Optional

try:
    from PyPDF2 import PdfReader
except ImportError:
    PdfReader = None

# Predefined skill sets per role
SKILLS_MAP = {
    "AI/ML Engineer": {
        "python", "machine learning", "deep learning", "tensorflow", "pytorch",
        "scikit-learn", "nlp", "computer vision", "neural networks", "keras",
        "data science", "statistics", "probability", "linear algebra", "calculus",
        "pandas", "numpy", "jupyter", "docker", "mlops", "kubernetes",
        "transformers", "langchain", "rag", "llm", "openai", "huggingface",
        "reinforcement learning", "time series", "feature engineering", "model deployment",
    },
    "Backend Engineer": {
        "python", "java", "go", "rust", "node.js", "typescript", "javascript",
        "fastapi", "flask", "django", "spring boot", "express",
        "postgresql", "mysql", "mongodb", "redis", "sql", "database",
        "docker", "kubernetes", "aws", "gcp", "azure", "ci/cd",
        "rest api", "graphql", "grpc", "microservices", "system design",
        "rabbitmq", "kafka", "nginx", "linux", "git", "testing",
    },
    "Data Scientist": {
        "python", "r", "sql", "statistics", "machine learning", "deep learning",
        "data analysis", "data visualization", "pandas", "numpy", "scikit-learn",
        "tensorflow", "pytorch", "tableau", "power bi", "excel",
        "a/b testing", "hypothesis testing", "regression", "classification",
        "clustering", "natural language processing", "time series",
        "feature engineering", "data cleaning", "etl", "spark", "hadoop",
    },
}

# Advanced / senior-level keywords that indicate deeper expertise
SENIOR_KEYWORDS = {
    "architecture", "design", "architect", "lead", "principal", "staff",
    "optimisation", "optimization", "scalability", "distributed systems",
    "high performance", "low latency", "trade-off", "tradeoff",
    "mentor", "tech lead", "team lead", "cross-functional",
    "strategy", "roadmap", "technical direction",
    "production", "deployment", "ci/cd", "monitoring", "observability",
}

# Mid-level keywords indicating practical implementation
MID_KEYWORDS = {
    "implemented", "built", "developed", "designed", "deployed",
    "integrated", "migrated", "refactored", "tested",
    "pipeline", "api", "microservice", "module", "component",
    "collaborated", "cross-team", "agile", "sprint",
    "sql", "database", "rest", "graphql", "docker", "kubernetes",
}


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text content from a PDF file."""
    if PdfReader is None:
        raise ImportError("PyPDF2 is required. Install with: pip install PyPDF2")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts)


def extract_skills(text: str, role: str) -> List[str]:
    """Extract known skills from resume text for a given role."""
    text_lower = text.lower()
    role_key = role.strip()
    skill_set = SKILLS_MAP.get(role_key, set())
    all_skills = set()
    for item in skill_set:
        if isinstance(item, (set, frozenset)):
            all_skills.update(item)
        else:
            all_skills.add(item)

    found = []
    for skill in all_skills:
        if skill.lower() in text_lower:
            found.append(skill)
    return found


def infer_experience_years(text: str) -> int:
    """
    Infer years of experience from resume text.
    Looks for patterns like 'X years of experience' or employment date ranges.
    """
    text_lower = text.lower()

    patterns = [
        r"(\d+)\+?\s*(?:years?|yrs?)\s*(?:of\s+)?(?:experience|exp)",
        r"experience\s*(?:of|:)?\s*(\d+)\+?\s*(?:years?|yrs?)",
    ]
    for pattern in patterns:
        matches = re.findall(pattern, text_lower)
        if matches:
            years = max(int(m) for m in matches)
            return min(years, 30)

    year_ranges = re.findall(r"(20\d{2})\s*[–\-to]+\s*(20\d{2}|present|current)", text_lower)
    if year_ranges:
        total_years = 0
        for start, end in year_ranges:
            start_year = int(start)
            if end in ("present", "current"):
                end_year = 2026
            else:
                end_year = int(end)
            total_years += max(0, end_year - start_year)
        return min(total_years, 30)

    return 0


def infer_difficulty(experience_years: int) -> str:
    """Map years of experience to overall difficulty level."""
    if experience_years < 2:
        return "easy"
    elif experience_years <= 5:
        return "medium"
    else:
        return "hard"


def compute_granular_scores(
    text: str,
    skills: List[str],
    experience_years: int,
) -> Tuple[int, int, int]:
    """
    Compute granular difficulty scores (0–10 each).

    Returns:
        (junior_score, mid_score, senior_score)

    Rules:
    - junior_score:  Based on breadth of fundamental skills matched.
    - mid_score:     Based on practical implementation keywords + years.
    - senior_score:  Based on architecture / leadership keywords + years.
    """
    text_lower = text.lower()

    # --- Junior score: breadth of known skills ---
    skill_count = len(skills)
    if skill_count >= 12:
        junior_score = 10
    elif skill_count >= 8:
        junior_score = 8
    elif skill_count >= 5:
        junior_score = 6
    elif skill_count >= 3:
        junior_score = 4
    else:
        junior_score = 2

    # --- Mid score: implementation experience ---
    mid_hits = sum(1 for kw in MID_KEYWORDS if kw in text_lower)
    mid_from_keywords = min(mid_hits * 2, 7)
    mid_from_years = min(experience_years, 3)
    mid_score = min(mid_from_keywords + mid_from_years, 10)

    # --- Senior score: architecture / leadership depth ---
    senior_hits = sum(1 for kw in SENIOR_KEYWORDS if kw in text_lower)
    senior_from_keywords = min(senior_hits * 2, 7)
    senior_from_years = min(max(experience_years - 3, 0), 3)  # only count years beyond 3
    senior_score = min(senior_from_keywords + senior_from_years, 10)

    return junior_score, mid_score, senior_score


def parse_resume(file_path: str, role: str) -> Tuple[str, List[str], int, str, int, int, int]:
    """
    Full pipeline: extract text, find skills, infer experience and difficulty,
    plus compute granular junior/mid/senior scores.

    Returns:
        (resume_text, skills_list, experience_years, difficulty,
         junior_score, mid_score, senior_score)
    """
    text = extract_text_from_pdf(file_path)
    skills = extract_skills(text, role)
    experience = infer_experience_years(text)
    difficulty = infer_difficulty(experience)
    junior_score, mid_score, senior_score = compute_granular_scores(text, skills, experience)
    return text, skills, experience, difficulty, junior_score, mid_score, senior_score