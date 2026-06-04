# AI-Powered Role-Based Candidate Screening System

An intelligent, AI-driven interview screening system that parses resumes, generates adaptive technical questions using RAG (Retrieval-Augmented Generation), evaluates answers in real-time, and produces structured hiring reports.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│   Next.js App   │────▶│  FastAPI Backend │────▶│   PostgreSQL  │
│   (Frontend)    │     │   (Python)       │     │   (Sessions)   │
└─────────────────┘     └────────┬─────────┘     └────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
           ┌──────────────────┐     ┌──────────────────┐
           │    Chroma DB     │     │    Groq LLM      │
           │  (Vector Store)  │     │ (mixtral-8x7b)   │
           └──────────────────┘     └──────────────────┘
                    ▲
                    │
           ┌──────────────────┐
           │  HuggingFace     │
           │  Embeddings      │
           │ (all-MiniLM-L6)  │
           └──────────────────┘
```

## Tech Stack

| Layer        | Technology                                        |
|--------------|---------------------------------------------------|
| Frontend     | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend      | FastAPI, Python 3.11+, SQLAlchemy 2.0 (async)     |
| Database     | PostgreSQL 15                                     |
| Vector DB    | ChromaDB (persistent, disk-based)                 |
| LLM          | Groq API — `mixtral-8x7b-32768` (free tier)       |
| Embeddings   | HuggingFace `sentence-transformers/all-MiniLM-L6-v2` (local, free) |
| RAG          | LangChain (document loading, text splitting, retrieval) |
| PDF Parsing  | PyPDF2                                            |

> **No paid embedding API needed.** Embeddings run locally via HuggingFace sentence-transformers. Only the Groq API key is required — free tier supports 30 req/min.

## Features

- **Resume Parsing** — Extracts text from PDF, identifies role-specific skills, infers experience level and difficulty (junior / mid / senior scores)
- **Adaptive RAG Questioning** — Groq LLM generates role-specific questions grounded in retrieved knowledge base chunks, adapting difficulty based on granular candidate scores
- **Answer Evaluation** — Each answer is scored 1–10 with strengths and weaknesses by the LLM
- **Full Traceability** — Every question logs the retrieval query and retrieved context chunks used to generate it
- **Session Management** — Complete interview state persisted in PostgreSQL with UUID-based sessions
- **AI Summary** — End-of-interview report with per-question scores and an overall hiring insight
- **Responsive UI** — Clean Next.js interface with progress tracking, drag-and-drop resume upload, and expandable Q&A summary cards

## Supported Roles

- AI/ML Engineer
- Backend Engineer
- Data Scientist

## Project Structure

```
ai-candidate-screener/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point + lifespan
│   │   ├── config.py                # Environment config (Settings class)
│   │   ├── database.py              # SQLAlchemy async engine + session factory
│   │   ├── models/
│   │   │   ├── session.py           # Session ORM model (difficulty scores, state)
│   │   │   └── qa.py                # QARecord ORM model (question, answer, eval)
│   │   ├── schemas/
│   │   │   ├── session.py           # Pydantic session schemas
│   │   │   ├── answer.py            # Answer request/response schemas
│   │   │   └── summary.py           # Summary response schema
│   │   ├── routers/
│   │   │   ├── upload.py            # POST /upload_resume
│   │   │   ├── interview.py         # POST /answer/{session_id}
│   │   │   └── summary.py           # GET /summary/{session_id}
│   │   └── services/
│   │       ├── resume_parser.py     # PDF text extraction + skill/difficulty inference
│   │       ├── knowledge_base.py    # ChromaDB + HuggingFace embeddings
│   │       ├── retrieval.py         # Dynamic query builder + context retrieval
│   │       ├── question_generator.py# Groq-powered adaptive question generation
│   │       ├── evaluator.py         # Groq-powered answer scoring
│   │       └── session_manager.py   # Interview flow orchestration
│   ├── data/
│   │   └── knowledge_base/          # Place reference PDFs here before ingesting
│   ├── ingest.py                    # CLI script to embed PDFs into ChromaDB
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # Home — resume upload + role selector
│   │   ├── interview/[session_id]/  # Adaptive interview page
│   │   └── summary/[session_id]/   # Final report page
│   ├── components/
│   │   ├── FileUpload.tsx           # Drag-and-drop PDF upload
│   │   ├── QuestionDisplay.tsx      # Question + difficulty badge
│   │   ├── AnswerInput.tsx          # Answer textarea
│   │   └── SummaryCard.tsx          # Expandable Q&A with scores
│   ├── lib/api.ts                   # Typed API client
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
├── DEMO_SCRIPT.md
└── README.md
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Groq API key (free at [console.groq.com](https://console.groq.com))

### 1. Clone and configure

```bash
git clone https://github.com/jv0019/AI-candidate-screening-system.git
cd AI-candidate-screening-system

cp .env.example .env
# Edit .env and set: GROQ_API_KEY=your-key-here
```

### 2. (Optional) Add knowledge base PDFs

Place reference PDFs (textbooks, documentation, etc.) in:

```
backend/data/knowledge_base/
```

The system works without them using fallback questions, but RAG quality improves significantly with relevant PDFs.

### 3. Start with Docker Compose

```bash
docker compose up --build
```

Starts:
- **PostgreSQL** on port 5432
- **FastAPI backend** on port 8000
- **Next.js frontend** on port 3000

### 4. Ingest knowledge base (optional)

```bash
cd backend
pip install -r requirements.txt
python ingest.py

# Custom directory or reset:
python ingest.py --dir /path/to/pdfs --reset
```

### 5. Open the app

Navigate to **http://localhost:3000**

## API Reference

| Method | Endpoint                | Description                                      |
|--------|-------------------------|--------------------------------------------------|
| POST   | `/upload_resume`        | Upload PDF + role → `session_id` + first question |
| POST   | `/answer/{session_id}`  | Submit answer → next question or finished flag   |
| GET    | `/summary/{session_id}` | Full Q&A log + per-answer scores + AI insight    |
| GET    | `/health`               | Health check                                     |

### Upload resume

```bash
curl -X POST http://localhost:8000/upload_resume \
  -F "file=@resume.pdf" \
  -F "role=AI/ML Engineer"
```

### Submit answer

```bash
curl -X POST http://localhost:8000/answer/{session_id} \
  -H "Content-Type: application/json" \
  -d '{"answer": "Your answer here"}'
```

### Get summary

```bash
curl http://localhost:8000/summary/{session_id}
```

## Environment Variables

| Variable                  | Default                                                                      | Description                          |
|---------------------------|------------------------------------------------------------------------------|--------------------------------------|
| `GROQ_API_KEY`            | `""`                                                                         | Groq API key (required)              |
| `GROQ_MODEL`              | `mixtral-8x7b-32768`                                                         | Groq model for question generation   |
| `GROQ_BASE_URL`           | `https://api.groq.com/openai/v1`                                             | Groq OpenAI-compatible endpoint      |
| `DATABASE_URL`            | `postgresql+asyncpg://postgres:postgres@localhost:5432/candidate_screener`   | PostgreSQL connection string         |
| `CHROMA_PERSIST_DIR`      | `./chroma_db`                                                                | ChromaDB persistence directory       |
| `MAX_QUESTIONS_PER_SESSION` | `10`                                                                       | Max questions per interview session  |
| `CHUNK_SIZE`              | `1000`                                                                       | Text chunk size for RAG ingestion    |
| `CHUNK_OVERLAP`           | `200`                                                                        | Chunk overlap for RAG ingestion      |
| `FRONTEND_URL`            | `http://localhost:3000`                                                       | CORS allowed origin                  |

## Running Without Docker

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env .env
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database

```bash
createdb candidate_screener
```

## How Difficulty Is Inferred

The resume parser assigns three granular scores (0–10) based on skill keywords and experience years:

| Score      | What it measures                                  |
|------------|---------------------------------------------------|
| `junior_score`  | Fundamental concept familiarity              |
| `mid_score`     | Practical implementation experience          |
| `senior_score`  | Architecture, design, and optimization depth |

The LLM uses all three scores to calibrate question depth — not just a single easy/medium/hard label.

## License

MIT
