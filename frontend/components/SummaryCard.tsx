"use client";

import { useState } from "react";

interface QAPairItem {
  question_index: number;
  question: string;
  answer: string | null;
  retrieval_query?: string | null;
  retrieved_context?: string | null;
  score?: number | null;
  strengths?: string | null;
  weaknesses?: string | null;
}

interface SummaryCardProps {
  qaPairs: QAPairItem[];
}

export default function SummaryCard({ qaPairs }: SummaryCardProps) {
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null);

  if (qaPairs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No questions were asked in this session.
      </div>
    );
  }

  const toggleExpand = (index: number) => {
    setExpandedIndex(expandedIndex === index ? null : index);
  };

  const getScoreColor = (score: number | null | undefined) => {
    if (!score) return "bg-gray-100 text-gray-600";
    if (score >= 8) return "bg-green-100 text-green-700";
    if (score >= 5) return "bg-yellow-100 text-yellow-700";
    return "bg-red-100 text-red-700";
  };

  return (
    <div className="space-y-6">
      {qaPairs.map((qa) => (
        <div
          key={qa.question_index}
          className="bg-white rounded-lg border border-gray-200 overflow-hidden"
        >
          {/* Header */}
          <div className="bg-gray-50 px-5 py-3 border-b border-gray-200 flex items-center justify-between">
            <span className="text-xs text-gray-500 font-medium">
              Question #{qa.question_index + 1}
            </span>
            <div className="flex items-center space-x-2">
              {qa.score && (
                <span
                  className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-bold ${getScoreColor(
                    qa.score
                  )}`}
                >
                  {qa.score}/10
                </span>
              )}
              <button
                onClick={() => toggleExpand(qa.question_index)}
                className="text-xs text-primary-600 hover:text-primary-800 font-medium"
              >
                {expandedIndex === qa.question_index ? "Less" : "Details"}
              </button>
            </div>
          </div>

          {/* Question & Answer */}
          <div className="px-5 py-4 space-y-3">
            <div>
              <p className="text-sm font-medium text-gray-700 mb-1">Question:</p>
              <p className="text-gray-900">{qa.question}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-700 mb-1">Answer:</p>
              {qa.answer ? (
                <p className="text-gray-800 whitespace-pre-wrap">{qa.answer}</p>
              ) : (
                <p className="text-gray-400 italic">Not answered</p>
              )}
            </div>
          </div>

          {/* Expanded Details: Evaluation + Traceability */}
          {expandedIndex === qa.question_index && (
            <div className="border-t border-gray-200 bg-gray-50/50">
              <div className="px-5 py-4 space-y-4">
                {/* Evaluation */}
                {(qa.strengths || qa.weaknesses) && (
                  <div>
                    <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                      Answer Evaluation
                    </h4>
                    {qa.strengths && (
                      <div className="mb-2">
                        <p className="text-xs font-medium text-green-700 mb-1">✓ Strengths</p>
                        <p className="text-xs text-gray-700 whitespace-pre-wrap">{qa.strengths}</p>
                      </div>
                    )}
                    {qa.weaknesses && (
                      <div>
                        <p className="text-xs font-medium text-red-700 mb-1">✗ Areas for Improvement</p>
                        <p className="text-xs text-gray-700 whitespace-pre-wrap">{qa.weaknesses}</p>
                      </div>
                    )}
                  </div>
                )}

                {/* Traceability */}
                {(qa.retrieval_query || qa.retrieved_context) && (
                  <div>
                    <h4 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">
                      Retrieval Traceability
                    </h4>
                    {qa.retrieval_query && (
                      <div className="mb-2">
                        <p className="text-xs font-medium text-gray-600 mb-1">Query:</p>
                        <pre className="text-xs text-gray-700 bg-white rounded p-2 border border-gray-200 overflow-x-auto">
                          {qa.retrieval_query}
                        </pre>
                      </div>
                    )}
                    {qa.retrieved_context && (
                      <div>
                        <p className="text-xs font-medium text-gray-600 mb-1">
                          Retrieved Context (top chunk):
                        </p>
                        <pre className="text-xs text-gray-700 bg-white rounded p-2 border border-gray-200 overflow-x-auto max-h-32 overflow-y-auto">
                          {qa.retrieved_context.substring(0, 600)}
                          {qa.retrieved_context.length > 600 && "..."}
                        </pre>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}