# AI-Powered Role-Based Candidate Screening System

An intelligent, AI-driven interview screening system that analyzes resumes, generates adaptive technical questions using RAG (Retrieval-Augmented Generation), and provides candidate assessments.

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│   Next.js App   │────▶│   FastAPI Backend │────▶│   PostgreSQL   │
│   (Frontend)    │     │   (Python)        │     │   (Sessions)   │
└─────────────────┘     └────────┬─────────┘     └────────────────┘
                                 │
                                 ▼
                        ┌──────────────────┐     ┌────────────────┐
                        │   Chroma DB      │◀───▶│   OpenAI API   │
                        │   (Vector Store)  │     │   (GPT + Emb)  │
                        └──────────────────┘     └────────────────┘
```

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router), TypeScript, Tailwind CSS |
| Backend | FastAPI, Python 3.11+, SQLAlchemy 2.0 (async) |
| Database | PostgreSQL 15 |
| Vector DB | Chroma (persistent, disk-based) |
| AI | OpenAI GPT-4o-mini, text-embedding-3-small |
| PDF Parsing | PyPDF2 |
| Text Splitting | langchain-community (RecursiveCharacterTextSplitter) |

## Features

- **Resume Parsing**: Extract text from PDF, identify skills per role, infer experience & difficulty
- **Adaptive Questioning**: GPT generates role-specific, difficulty-adapted technical questions
- **RAG Pipeline**: Knowledge base PDFs → chunked → embedded → retrieved context for better questions
- **Session Management**: Full interview state persisted in PostgreSQL
- **AI Summary**: Complete Q&A log with AI-generated insight and hiring recommendation
- **Responsive UI**: Modern, clean interface with progress tracking

## Project Structure

```
ai-candidate-screener/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI entry point
│   │   ├── config.py            # Environment config
│   │   ├── database.py          # SQLAlchemy async setup
│   │   ├── models/              # ORM models (Session, QARecord)
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routers/             # API routes (upload, interview, summary)
│   │   └── services/            # Business logic
│   │       ├── resume_parser.py
│   │       ├── knowledge_base.py
│   │       ├── retrieval.py
│   │       ├── question_generator.py
│   │       └── session_manager.py
│   ├── data/
│   │   └── knowledge_base/      # Place PDF knowledge files here
│   ├── ingest.py                # Knowledge base ingestion script
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Home - upload + role selector
│   │   ├── layout.tsx
│   │   ├── globals.css
│   │   ├── interview/[session_id]/page.tsx
│   │   └── summary/[session_id]/page.tsx
│   ├── components/
│   │   ├── FileUpload.tsx
│   │   ├── QuestionDisplay.tsx
│   │   ├── AnswerInput.tsx
│   │   └── SummaryCard.tsx
│   ├── lib/api.ts               # API client
│   ├── package.json
│   ├── Dockerfile
│   └── next.config.js
├── docker-compose.yml
├── .env.example
├── README.md
└── DEMO_SCRIPT.md
```

## Quick Start

### Prerequisites

- Docker & Docker Compose
- OpenAI API key

### 1. Clone and Setup

```bash
git clone <repo-url>
cd ai-candidate-screener

# Copy environment file and add your OpenAI key
cp .env.example .env
# Edit .env: set OPENAI_API_KEY=sk-your-key-here
```

### 2. Add Knowledge Base PDFs (Optional but Recommended)

Place your reference PDFs (ML books, documentation, etc.) in:

```bash
backend/data/knowledge_base/
```

If no PDFs are present, the system will use mock mode with fallback questions.

### 3. Start with Docker Compose

```bash
docker compose up --build
```

This starts:
- **PostgreSQL** on port 5432
- **FastAPI backend** on port 8000
- **Next.js frontend** on port 3000

### 4. Ingest Knowledge Base (Optional)

After the stack is running, run the ingestion script:

```bash
cd backend
pip install -r requirements.txt
python ingest.py
```

Or ingest specific PDFs:

```bash
python ingest.py --dir /path/to/pdf/files --reset
```

### 5. Open the Application

Navigate to **http://localhost:3000**

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/upload_resume` | Upload PDF + role → session_id + first question |
| POST | `/answer/{session_id}` | Submit answer → next question or finished |
| GET | `/summary/{session_id}` | Full Q&A log + AI insight |
| GET | `/health` | Health check |

### Example: Upload Resume

```bash
curl -X POST http://localhost:8000/upload_resume \
  -F "file=@resume.pdf" \
  -F "role=AI/ML Engineer"
```

### Example: Submit Answer

```bash
curl -X POST http://localhost:8000/answer/{session_id} \
  -H "Content-Type: application/json" \
  -d '{"answer": "My answer here..."}'
```

### Example: Get Summary

```bash
curl http://localhost:8000/summary/{session_id}
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | `""` | Your OpenAI API key |
| `DATABASE_URL` | `postgresql+asyncpg://postgres:postgres@localhost:5432/candidate_screener` | PostgreSQL connection string |
| `OPENAI_MODEL` | `gpt-4o-mini` | Model for question generation |
| `OPENAI_EMBEDDING_MODEL` | `text-embedding-3-small` | Model for embeddings |
| `CHROMA_PERSIST_DIR` | `./chroma_db` | Chroma persistence directory |
| `MAX_QUESTIONS_PER_SESSION` | `10` | Maximum questions per interview |
| `FRONTEND_URL` | `http://localhost:3000` | CORS allowed origin |

## Running Without Docker

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env .env  # or set env vars directly
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Database

Make sure PostgreSQL is running locally and the database exists:

```bash
createdb candidate_screener
```

## Skill Extraction

The system uses predefined keyword sets per role:

- **AI/ML Engineer**: python, tensorflow, pytorch, nlp, computer vision, transformers, langchain, RAG, etc.
- **Backend Engineer**: python, java, go, fastapi, postgresql, docker, kubernetes, microservices, etc.
- **Data Scientist**: python, r, statistics, machine learning, data visualization, a/b testing, etc.

## Difficulty Inference

| Experience | Difficulty | Question Style |
|---|---|---|
| 0–1 years | Easy | Fundamentals, concepts, basic implementations |
| 2–5 years | Medium | Problem-solving, design decisions, trade-offs |
| 6+ years | Hard | System design, optimization, research-level |

## License

MIT