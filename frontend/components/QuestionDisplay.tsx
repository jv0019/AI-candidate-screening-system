"use client";

interface QuestionDisplayProps {
  question: string;
  questionIndex: number;
  totalQuestions: number;
  role: string;
  difficulty: string;
  skills: string;
}

export default function QuestionDisplay({
  question,
  questionIndex,
  totalQuestions,
  role,
  difficulty,
  skills,
}: QuestionDisplayProps) {
  const difficultyColors: Record<string, string> = {
    easy: "bg-green-100 text-green-800",
    medium: "bg-yellow-100 text-yellow-800",
    hard: "bg-red-100 text-red-800",
  };

  return (
    <div className="bg-white rounded-xl shadow-md p-6 space-y-4">
      {/* Session Info */}
      <div className="flex flex-wrap items-center gap-3 text-sm">
        <span className="px-3 py-1 bg-primary-100 text-primary-700 rounded-full font-medium">
          {role}
        </span>
        <span
          className={`px-3 py-1 rounded-full font-medium capitalize ${
            difficultyColors[difficulty] || "bg-gray-100 text-gray-800"
          }`}
        >
          {difficulty}
        </span>
        {skills && (
          <span className="text-gray-500">
            Skills: {skills}
          </span>
        )}
      </div>

      {/* Progress */}
      <div className="flex items-center space-x-2">
        <div className="flex-1 bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all duration-500"
            style={{
              width: `${totalQuestions > 0 ? ((questionIndex + 1) / totalQuestions) * 100 : 10}%`,
            }}
          />
        </div>
        <span className="text-xs text-gray-500 font-medium">
          Question {questionIndex + 1} of {totalQuestions}
        </span>
      </div>

      {/* Question */}
      <div className="pt-2">
        <h2 className="text-lg font-semibold text-gray-900 mb-3">
          Interview Question
        </h2>
        <div className="bg-gray-50 rounded-lg p-5 border border-gray-200">
          <p className="text-gray-800 text-base leading-relaxed">{question}</p>
        </div>
      </div>
    </div>
  );
}