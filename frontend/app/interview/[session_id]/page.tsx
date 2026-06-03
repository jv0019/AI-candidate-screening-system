"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import QuestionDisplay from "@/components/QuestionDisplay";
import AnswerInput from "@/components/AnswerInput";
import { submitAnswer, getSummary } from "@/lib/api";

interface InterviewState {
  sessionId: string;
  role: string;
  skills: string;
  difficulty: string;
  currentQuestion: string;
  questionIndex: number;
  totalQuestions: number;
  finished: boolean;
}

export default function InterviewPage() {
  const params = useParams();
  const router = useRouter();
  const sessionId = params.session_id as string;

  const [state, setState] = useState<InterviewState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Initialize state from sessionStorage or URL params
  useEffect(() => {
    if (!sessionId) return;

    // Check if we have stored session data
    const stored = sessionStorage.getItem(`session_${sessionId}`);
    if (stored) {
      const parsed = JSON.parse(stored);
      setState(parsed);
      return;
    }

    // If we're redirected from upload, try to get session info
    try {
      const initialData = {
        sessionId,
        role: "Unknown",
        skills: "",
        difficulty: "medium",
        currentQuestion: "Loading question...",
        questionIndex: 0,
        totalQuestions: 10,
        finished: false,
      };
      setState(initialData);
      sessionStorage.setItem(`session_${sessionId}`, JSON.stringify(initialData));
    } catch (err) {
      setError("Failed to initialize interview session.");
    }
  }, [sessionId]);

  // Persist state changes
  const updateState = useCallback(
    (updates: Partial<InterviewState>) => {
      setState((prev) => {
        if (!prev) return prev;
        const newState = { ...prev, ...updates };
        sessionStorage.setItem(`session_${sessionId}`, JSON.stringify(newState));
        return newState;
      });
    },
    [sessionId]
  );

  const handleSubmitAnswer = async (answer: string) => {
    if (!state) return;
    setLoading(true);
    setError(null);

    try {
      const result = await submitAnswer(sessionId, answer);

      if (result.finished) {
        updateState({
          finished: true,
          questionIndex: result.question_index,
        });
        // Redirect to summary after short delay
        setTimeout(() => {
          router.push(`/summary/${sessionId}`);
        }, 1500);
      } else if (result.next_question) {
        updateState({
          currentQuestion: result.next_question,
          questionIndex: result.question_index,
        });
      }
    } catch (err: any) {
      setError(err.message || "Failed to submit answer. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (!state) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <svg className="animate-spin h-10 w-10 text-primary-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-gray-500">Loading interview session...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      {/* Error Banner */}
      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div className="flex-1">
              <p className="text-sm text-red-700">{error}</p>
              <button
                onClick={() => setError(null)}
                className="text-sm text-red-600 underline mt-1"
              >
                Dismiss
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Finished Banner */}
      {state.finished && (
        <div className="p-6 bg-green-50 border border-green-200 rounded-lg text-center">
          <svg className="w-12 h-12 text-green-500 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h2 className="text-xl font-semibold text-green-800 mb-2">
            Interview Complete!
          </h2>
          <p className="text-green-600 mb-4">
            Redirecting to your summary...
          </p>
        </div>
      )}

      {/* Question Display */}
      {!state.finished && (
        <QuestionDisplay
          question={state.currentQuestion}
          questionIndex={state.questionIndex}
          totalQuestions={state.totalQuestions}
          role={state.role}
          difficulty={state.difficulty}
          skills={state.skills}
        />
      )}

      {/* Answer Input */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <AnswerInput
          onSubmit={handleSubmitAnswer}
          loading={loading}
          finished={state.finished}
        />
      </div>
    </div>
  );
}