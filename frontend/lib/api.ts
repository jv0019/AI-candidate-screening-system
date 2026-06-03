const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface UploadResponse {
  session_id: string;
  role: string;
  skills: string;
  experience_years: number;
  difficulty: string;
  junior_score?: number;
  mid_score?: number;
  senior_score?: number;
  question_index: number;
  question: string;
  finished: boolean;
}

export interface AnswerResponse {
  session_id: string;
  question_index: number;
  next_question?: string;
  finished: boolean;
  message?: string;
}

export interface QAPair {
  question_index: number;
  question: string;
  answer: string | null;
  retrieval_query?: string | null;
  retrieved_context?: string | null;
  score?: number | null;
  strengths?: string | null;
  weaknesses?: string | null;
}

export interface SummaryResponse {
  session_id: string;
  role: string;
  skills: string;
  experience_years: number;
  difficulty: string;
  junior_score?: number;
  mid_score?: number;
  senior_score?: number;
  total_questions: number;
  qa_pairs: QAPair[];
  insight: string;
}

export async function uploadResume(
  file: File,
  role: string
): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("role", role);

  const response = await fetch(`${API_BASE_URL}/upload_resume`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to upload resume");
  }

  return response.json();
}

export async function submitAnswer(
  sessionId: string,
  answer: string
): Promise<AnswerResponse> {
  const response = await fetch(`${API_BASE_URL}/answer/${sessionId}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ answer }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to submit answer");
  }

  return response.json();
}

export async function getSummary(
  sessionId: string
): Promise<SummaryResponse> {
  const response = await fetch(`${API_BASE_URL}/summary/${sessionId}`, {
    method: "GET",
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || "Failed to get summary");
  }

  return response.json();
}