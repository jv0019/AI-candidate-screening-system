# 🤖 AI-Powered Role-Based Candidate Screening System

An end-to-end AI interview platform that automatically analyzes resumes, generates adaptive technical interview questions using Retrieval-Augmented Generation (RAG), evaluates candidate responses in real time, and produces structured hiring reports.

Built with **FastAPI**, **Next.js**, **LangChain**, **ChromaDB**, **Groq LLMs**, and **PostgreSQL**, the system simulates the first stage of a technical hiring process while maintaining transparency through retrieval traceability and detailed evaluation reports.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![RAG](https://img.shields.io/badge/AI-RAG-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)

---

## 🚀 Key Highlights

* 📄 Resume Parsing & Skill Extraction
* 🧠 Adaptive AI Interview Generation
* 🔍 Retrieval-Augmented Generation (RAG)
* 📊 Real-Time Answer Evaluation
* 📝 AI-Generated Hiring Reports
* 🗄 Persistent Interview Sessions
* 📈 Difficulty Calibration Based on Candidate Profile
* 🔎 Full Retrieval Traceability for Every Question

---

## 🎯 Business Problem

Recruiters and hiring managers often spend significant time conducting initial technical screenings. Generic interview questions frequently fail to accurately assess a candidate's actual skills and experience.

This system addresses that challenge by:

* Parsing resumes automatically
* Identifying role-specific skills
* Generating contextual technical questions
* Dynamically adjusting interview difficulty
* Scoring answers consistently
* Producing structured hiring summaries

The result is a scalable and repeatable AI-assisted technical screening workflow.

---

## 🏗 System Architecture

```text
┌─────────────────┐     ┌──────────────────┐     ┌────────────────┐
│   Next.js App   │────▶│  FastAPI Backend │────▶│   PostgreSQL   │
│   (Frontend)    │     │     (Python)     │     │   (Sessions)   │
└─────────────────┘     └────────┬─────────┘     └────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
           ┌──────────────────┐     ┌──────────────────┐
           │    ChromaDB      │     │     Groq LLM     │
           │  Vector Store    │     │  mixtral-8x7b    │
           └──────────────────┘     └──────────────────┘
                    ▲
                    │
           ┌──────────────────┐
           │ HuggingFace      │
           │ Embeddings       │
           │ all-MiniLM-L6-v2 │
           └──────────────────┘
```

---

## ✨ Features

### 📄 Resume Intelligence

* Extracts text from uploaded PDF resumes
* Detects technical skills and domain expertise
* Estimates experience level and interview difficulty
* Generates candidate-specific interview paths

### 🧠 Adaptive AI Interview Engine

* Role-aware technical questioning
* Dynamic difficulty adjustment
* Retrieval-grounded question generation
* Reduced hallucinations through contextual retrieval

### 🔍 Retrieval-Augmented Generation (RAG)

* Vector search using ChromaDB
* Semantic retrieval using HuggingFace embeddings
* Context-aware question generation
* Support for custom knowledge bases

### 📊 Answer Evaluation

* Scores answers on a 1–10 scale
* Identifies strengths and weaknesses
* Provides structured evaluation feedback
* Maintains consistency across interview sessions

### 🗂 Interview Session Management

* UUID-based interview sessions
* PostgreSQL persistence
* Complete interview state tracking
* Recovery and reporting support

### 📝 AI Hiring Reports

* Per-question evaluations
* Aggregate performance scoring
* Candidate strengths and weaknesses
* Hiring recommendation insights

### 🔎 Full Explainability

Every generated question stores:

* Retrieval query
* Retrieved document chunks
* Generated question
* Candidate answer
* Evaluation result

This creates a fully auditable interview trail.

---

## 👨‍💻 Supported Roles

Currently supported:

* AI / ML Engineer
* Backend Engineer
* Data Scientist

Additional roles can be added through knowledge-base expansion and prompt configuration.

---

## 🛠 Technology Stack

| Layer            | Technology                            |
| ---------------- | ------------------------------------- |
| Frontend         | Next.js 14, TypeScript, Tailwind CSS  |
| Backend          | FastAPI, Python 3.11+, SQLAlchemy 2.0 |
| Database         | PostgreSQL 15                         |
| Vector Database  | ChromaDB                              |
| Embeddings       | HuggingFace Sentence Transformers     |
| LLM              | Groq Mixtral-8x7B                     |
| RAG Framework    | LangChain                             |
| PDF Processing   | PyPDF2                                |
| Containerization | Docker & Docker Compose               |

---

## 📂 Project Structure

```text
ai-candidate-screener/
│
├── backend/
│   ├── app/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── models/
│   │   ├── database.py
│   │   ├── config.py
│   │   └── main.py
│   │
│   ├── data/
│   │   └── knowledge_base/
│   │
│   ├── ingest.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── Dockerfile
│
├── docker-compose.yml
├── .env.example
├── DEMO_SCRIPT.md
└── README.md
```

---

## ⚙️ Quick Start

### Prerequisites

* Docker
* Docker Compose
* Groq API Key

### Clone Repository

```bash
git clone https://github.com/jv0019/AI-candidate-screening-system.git
cd AI-candidate-screening-system
```

### Configure Environment

```bash
cp .env.example .env
```

Add your Groq API key:

```env
GROQ_API_KEY=your_api_key_here
```

### Start Services

```bash
docker compose up --build
```

Services launched:

| Service    | Port |
| ---------- | ---- |
| Frontend   | 3000 |
| Backend    | 8000 |
| PostgreSQL | 5432 |

### Open Application

```text
http://localhost:3000
```

---

## 📚 Knowledge Base Ingestion

Place PDFs into:

```text
backend/data/knowledge_base/
```

Then ingest:

```bash
cd backend
python ingest.py
```

Optional:

```bash
python ingest.py --dir /path/to/pdfs --reset
```

---

## 🔌 API Endpoints

| Method | Endpoint                | Description                             |
| ------ | ----------------------- | --------------------------------------- |
| POST   | `/upload_resume`        | Upload resume and create interview      |
| POST   | `/answer/{session_id}`  | Submit answer and receive next question |
| GET    | `/summary/{session_id}` | Retrieve final evaluation report        |
| GET    | `/health`               | Service health check                    |

---

## 🎯 Difficulty Scoring System

Instead of using a simple Easy / Medium / Hard classification, the system maintains three independent capability scores:

| Score        | Purpose                                   |
| ------------ | ----------------------------------------- |
| Junior Score | Fundamental technical knowledge           |
| Mid Score    | Practical implementation experience       |
| Senior Score | System design and architectural expertise |

These scores are continuously used to calibrate interview difficulty and question depth.

---

## 🔒 Design Goals

* Transparent AI decision-making
* Explainable question generation
* Retrieval-grounded evaluations
* Scalable interview workflows
* Consistent candidate assessment
* Minimal operational cost

---

## 📈 Future Enhancements

* [ ] Multi-agent interview orchestration
* [ ] Voice-based interviewing
* [ ] Live coding assessments
* [ ] ATS integration
* [ ] Multi-role interview pipelines
* [ ] Recruiter analytics dashboard
* [ ] Candidate benchmarking
* [ ] Interview replay functionality

---

## 📜 License

MIT License

---

## 👤 Author

**Jivitesh Sachdev**

Software Development • AI Engineering • RAG Systems • ESG Analytics

GitHub: https://github.com/jv0019

---

### Keywords

Artificial Intelligence • RAG • LangChain • FastAPI • Next.js • LLM Applications • Candidate Screening • Interview Automation • ChromaDB • Vector Search • Groq • AI Recruiting • Retrieval-Augmented Generation
