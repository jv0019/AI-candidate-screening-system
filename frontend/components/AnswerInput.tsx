"use client";

import { useState } from "react";

interface AnswerInputProps {
  onSubmit: (answer: string) => Promise<void>;
  loading: boolean;
  finished: boolean;
}

export default function AnswerInput({
  onSubmit,
  loading,
  finished,
}: AnswerInputProps) {
  const [answer, setAnswer] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!answer.trim() || loading || finished) return;
    await onSubmit(answer.trim());
    setAnswer("");
  };

  if (finished) {
    return null;
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label
          htmlFor="answer"
          className="block text-sm font-medium text-gray-700 mb-2"
        >
          Your Answer
        </label>
        <textarea
          id="answer"
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
          rows={5}
          placeholder="Type your answer here..."
          className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-base resize-none"
          disabled={loading}
        />
      </div>

      <div className="flex items-center justify-between">
        <p className="text-xs text-gray-400">
          {answer.length} characters
        </p>
        <button
          type="submit"
          disabled={!answer.trim() || loading}
          className={`px-6 py-2.5 rounded-lg font-semibold text-white transition-colors ${
            answer.trim() && !loading
              ? "bg-primary-600 hover:bg-primary-700"
              : "bg-gray-300 cursor-not-allowed"
          }`}
        >
          {loading ? (
            <span className="flex items-center space-x-2">
              <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <span>Generating Next Question...</span>
            </span>
          ) : (
            "Submit Answer"
          )}
        </button>
      </div>
    </form>
  );
}