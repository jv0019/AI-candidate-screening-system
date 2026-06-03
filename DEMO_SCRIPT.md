# Demo Video Script (5-Minute Walkthrough)

## Title: AI-Powered Role-Based Candidate Screening System

**Duration:** ~5 minutes
**Presenter:** Developer

---

### [0:00–0:30] Introduction & Overview

**Visual:** Home page of the application showing the title "AI-Powered Candidate Screening"

**Script:**
> "Welcome to the AI-powered role-based candidate screening system. This tool analyzes resumes, generates adaptive technical interview questions using a RAG pipeline with OpenAI and Chroma vector database, and provides an AI-powered candidate assessment summary."
>
> "You can see we have three target roles to choose from: AI/ML Engineer, Backend Engineer, and Data Scientist. The system will parse the uploaded resume, extract skills, infer experience level, and adjust question difficulty accordingly."

---

### [0:30–1:15] Step 1: Upload a Resume

**Visual:** Select "AI/ML Engineer" from dropdown → drag-and-drop a PDF resume → click "Start Interview"

**Script:**
> "Let's start by screening a candidate for an AI/ML Engineer position. I'll select the role from the dropdown, then upload a candidate's resume PDF. You can either drag and drop the file or click to browse."
>
> "I'll upload this sample resume. Once selected, I click 'Start Interview' which triggers the backend to parse the PDF, extract skills like Python, TensorFlow, and NLP, and infer the candidate's experience level to determine question difficulty."

---

### [1:15–2:30] Step 2: First Interview Question

**Visual:** Transition to interview page showing the first question with role badge, difficulty indicator, and progress bar

**Script:**
> "The system has processed the resume and generated a first question. Notice the UI shows the role badge 'AI/ML Engineer', the difficulty level, and the detected skills from the resume."
>
> "The question is specifically tailored to this candidate's profile. It uses our RAG pipeline — the system constructed a query from the candidate's skills plus the target role, retrieved relevant chunks from our knowledge base of ML books stored in Chroma, and fed that context to GPT-4o-mini to generate this focused technical question."
>
> "Let's type an answer and submit it."

**Visual:** Type an answer in the textarea, click "Submit Answer"

---

### [2:30–3:30] Step 3: Adaptive Follow-Up

**Visual:** Loading spinner → new question appears

**Script:**
> "The backend received our answer, stored it in PostgreSQL along with the original question, and then constructed a dynamic query that includes the previous Q&A context. This allows the next question to adapt based on what the candidate just said."
>
> "Notice how the progress bar advanced — this is question 2 of 10. The system uses adaptive questioning to go deeper into topics the candidate seems strong in, or pivot if they're struggling."
>
> "Let's answer a few more questions to build up a good interview history."

**Visual:** Quick-motion of answering 2-3 more questions (accelerated)

---

### [3:30–4:15] Step 4: Interview Completion

**Visual:** Green success banner "Interview Complete!" → auto-redirect to summary page

**Script:**
> "After the maximum questions are reached, the system marks the session as finished and redirects to the summary page."
>
> "Now we can see the complete interview summary. At the top, we have session metadata — the role, difficulty level, inferred years of experience, and total questions asked."
>
> "Below that, the detected skills are displayed as tags. These were matched against our predefined skill sets during the PDF parsing phase."

---

### [4:15–5:00] Step 5: AI Assessment & Transcript

**Visual:** Scrolling through the AI insight section → showing the Q&A transcript

**Script:**
> "Here's the AI-generated assessment. GPT analyzed all the Q&A pairs and produced an objective evaluation including overall knowledge assessment, key strengths, areas for improvement, and a hiring recommendation."
>
> "Below that, we have the full interview transcript showing every question and answer from the session."
>
> "The 'Screen Another Candidate' button lets us start a new screening immediately."
>
> "This system demonstrates how AI and RAG can streamline technical screening — it's role-specific, adaptive, and provides structured, objective assessments. Thanks for watching!"

---

## Key Talking Points for the Demo

| Segment | What to Highlight |
|---|---|
| **Upload** | PDF parsing, skill extraction, difficulty inference |
| **First Question** | RAG pipeline: query construction → Chroma retrieval → GPT generation |
| **Follow-up** | Adaptive questioning with previous Q&A context |
| **Completion** | Session management, max questions enforcement |
| **Summary** | AI-generated insight with structured assessment |

## Technical Notes for Recording

1. Have a sample resume PDF ready beforehand (any technical resume works)
2. Ensure OpenAI API key is set in `.env` and the backend is running
3. For the accelerated portion, consider screen recording at normal speed then speeding up in editing
4. If OCR/text extraction fails on the sample PDF, prepare a brief fallback explanation
5. The fallback questions will work even without knowledge base PDFs ingested

## Sample Resume for Demo

Create a simple text-based PDF with content like:

```
John Doe
AI/ML Engineer | 4 years experience

Skills: Python, TensorFlow, PyTorch, NLP, Computer Vision, Docker, Kubernetes

Experience:
- ML Engineer at TechCorp (2022-2025): Built NLP pipelines, deployed models
- Data Scientist at DataInc (2020-2022): Developed ML models, A/B testing

Education: MS in Computer Science