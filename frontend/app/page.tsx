"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import FileUpload from "@/components/FileUpload";
import { uploadResume } from "@/lib/api";

export default function HomePage() {
  const router = useRouter();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleUpload = async (file: File, role: string) => {
  setLoading(true);
  setError(null);

  try {
    const result = await uploadResume(file, role);
    
    // Save session data so interview page can use it
    sessionStorage.setItem(`session_${result.session_id}`, JSON.stringify({
      sessionId: result.session_id,
      role: result.role,
      skills: result.skills,
      difficulty: result.difficulty,
      currentQuestion: result.question,
      questionIndex: result.question_index,
      totalQuestions: 10,
      finished: result.finished,
    }));

    router.push(`/interview/${result.session_id}`);
  } catch (err: any) {
    setError(err.message || "Failed to process resume. Please try again.");
  } finally {
    setLoading(false);
  }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center">
      <div className="w-full max-w-lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-3">
            AI-Powered Candidate Screening
          </h1>
          <p className="text-gray-600">
            Upload a resume and select a target role to begin an intelligent,
            adaptive interview powered by AI and RAG.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8">
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-start space-x-2">
                <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          <FileUpload onUpload={handleUpload} loading={loading} />
        </div>

        <div className="mt-6 text-center">
          <p className="text-xs text-gray-400">
            Your resume is processed securely and used only for generating interview questions.
          </p>
        </div>
      </div>
    </div>
  );
}