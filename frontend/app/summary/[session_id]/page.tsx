"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import SummaryCard from "@/components/SummaryCard";
import { getSummary, SummaryResponse } from "@/lib/api";

export default function SummaryPage() {
  const params = useParams();
  const sessionId = params.session_id as string;

  const [summary, setSummary] = useState<SummaryResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) return;

    const fetchSummary = async () => {
      try {
        const data = await getSummary(sessionId);
        setSummary(data);
        sessionStorage.removeItem(`session_${sessionId}`);
      } catch (err: any) {
        setError(err.message || "Failed to load summary.");
      } finally {
        setLoading(false);
      }
    };

    fetchSummary();
  }, [sessionId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <svg className="animate-spin h-10 w-10 text-primary-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
          </svg>
          <p className="text-gray-500">Generating your interview summary...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-3xl mx-auto">
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <svg className="w-5 h-5 text-red-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="text-sm text-red-700">{error}</p>
              <Link href="/" className="text-sm text-red-600 underline mt-2 inline-block">
                Return to home
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  const difficultyColors: Record<string, string> = {
    easy: "bg-green-100 text-green-800",
    medium: "bg-yellow-100 text-yellow-800",
    hard: "bg-red-100 text-red-800",
  };

  const getScoreColor = (score: number | undefined | null) => {
    if (!score) return "bg-gray-100 text-gray-600";
    if (score >= 7) return "bg-green-100 text-green-700";
    if (score >= 4) return "bg-yellow-100 text-yellow-700";
    return "bg-red-100 text-red-700";
  };

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Interview Summary
        </h1>
        <p className="text-gray-500">
          Complete review of the candidate screening session
        </p>
      </div>

      {/* Session Info Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <p className="text-xs text-gray-500 uppercase font-medium mb-1">Role</p>
          <p className="text-sm font-semibold text-gray-900">{summary.role}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <p className="text-xs text-gray-500 uppercase font-medium mb-1">Difficulty</p>
          <span
            className={`inline-block px-2 py-1 rounded-full text-xs font-medium capitalize ${
              difficultyColors[summary.difficulty] || "bg-gray-100 text-gray-800"
            }`}
          >
            {summary.difficulty}
          </span>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <p className="text-xs text-gray-500 uppercase font-medium mb-1">Experience</p>
          <p className="text-sm font-semibold text-gray-900">
            {summary.experience_years} years
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-4 border border-gray-200">
          <p className="text-xs text-gray-500 uppercase font-medium mb-1">Questions</p>
          <p className="text-sm font-semibold text-gray-900">{summary.total_questions}</p>
        </div>
      </div>

      {/* Granular Difficulty Scores */}
      {(summary.junior_score !== undefined || summary.mid_score !== undefined || summary.senior_score !== undefined) && (
        <div className="bg-white rounded-lg shadow-sm p-5 border border-gray-200">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Resume-Aware Difficulty Profile</h2>
          <div className="flex flex-wrap gap-4">
            <div className="flex-1 min-w-[120px]">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500">Junior (Fundamentals)</span>
                <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${getScoreColor(summary.junior_score)}`}>
                  {summary.junior_score ?? "—"}/10
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all"
                  style={{ width: `${((summary.junior_score ?? 0) / 10) * 100}%` }}
                />
              </div>
            </div>
            <div className="flex-1 min-w-[120px]">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500">Mid (Implementation)</span>
                <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${getScoreColor(summary.mid_score)}`}>
                  {summary.mid_score ?? "—"}/10
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-yellow-500 h-2 rounded-full transition-all"
                  style={{ width: `${((summary.mid_score ?? 0) / 10) * 100}%` }}
                />
              </div>
            </div>
            <div className="flex-1 min-w-[120px]">
              <div className="flex items-center justify-between mb-1">
                <span className="text-xs text-gray-500">Senior (Architecture)</span>
                <span className={`text-xs font-bold px-1.5 py-0.5 rounded ${getScoreColor(summary.senior_score)}`}>
                  {summary.senior_score ?? "—"}/10
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full transition-all"
                  style={{ width: `${((summary.senior_score ?? 0) / 10) * 100}%` }}
                />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Skills */}
      {summary.skills && (
        <div className="bg-white rounded-lg shadow-sm p-5 border border-gray-200">
          <h2 className="text-sm font-semibold text-gray-700 mb-3">Detected Skills</h2>
          <div className="flex flex-wrap gap-2">
            {summary.skills.split(", ").map((skill, i) => (
              <span
                key={i}
                className="px-3 py-1 bg-primary-50 text-primary-700 rounded-full text-xs font-medium"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* AI Insight */}
      {summary.insight && (
        <div className="bg-gradient-to-r from-primary-50 to-blue-50 rounded-xl shadow-sm p-6 border border-primary-200">
          <div className="flex items-start space-x-3">
            <svg className="w-6 h-6 text-primary-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <div>
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                AI Assessment & Insights
              </h2>
              <div className="prose prose-sm text-gray-700 whitespace-pre-wrap">
                {summary.insight}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Q&A Log */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Full Interview Transcript
        </h2>
        <SummaryCard qaPairs={summary.qa_pairs} />
      </div>

      {/* Actions */}
      <div className="text-center pb-8">
        <Link
          href="/"
          className="inline-flex items-center px-6 py-3 bg-primary-600 text-white font-semibold rounded-lg hover:bg-primary-700 transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Screen Another Candidate
        </Link>
      </div>
    </div>
  );
}