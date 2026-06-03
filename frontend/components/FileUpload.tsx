"use client";

import { useState, useRef } from "react";

interface FileUploadProps {
  onUpload: (file: File, role: string) => Promise<void>;
  loading: boolean;
}

const ROLES = ["AI/ML Engineer", "Backend Engineer", "Data Scientist"];

export default function FileUpload({ onUpload, loading }: FileUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [role, setRole] = useState<string>("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0] || null;
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);
    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile && droppedFile.type === "application/pdf") {
      setFile(droppedFile);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file || !role) return;
    await onUpload(file, role);
  };

  const isFormValid = file && role;

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Role Selector */}
      <div>
        <label htmlFor="role" className="block text-sm font-medium text-gray-700 mb-2">
          Target Role
        </label>
        <select
          id="role"
          value={role}
          onChange={(e) => setRole(e.target.value)}
          className="w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-base"
          required
        >
          <option value="">Select a role...</option>
          {ROLES.map((r) => (
            <option key={r} value={r}>
              {r}
            </option>
          ))}
        </select>
      </div>

      {/* File Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Upload Resume (PDF)
        </label>
        <div
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            dragOver
              ? "border-primary-500 bg-primary-50"
              : file
              ? "border-green-400 bg-green-50"
              : "border-gray-300 hover:border-gray-400"
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf"
            onChange={handleFileChange}
            className="hidden"
          />
          {file ? (
            <div className="space-y-2">
              <svg className="mx-auto h-12 w-12 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <p className="text-sm font-medium text-green-600">{file.name}</p>
              <p className="text-xs text-gray-500">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
              <button
                type="button"
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                }}
                className="text-xs text-red-500 hover:text-red-700 underline"
              >
                Remove
              </button>
            </div>
          ) : (
            <div className="space-y-2">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              <p className="text-sm text-gray-600">
                Drop your resume PDF here, or click to browse
              </p>
              <p className="text-xs text-gray-400">PDF only, max 10MB</p>
            </div>
          )}
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={!isFormValid || loading}
        className={`w-full py-3 px-6 rounded-lg font-semibold text-white transition-colors ${
          isFormValid && !loading
            ? "bg-primary-600 hover:bg-primary-700"
            : "bg-gray-300 cursor-not-allowed"
        }`}
      >
        {loading ? (
          <span className="flex items-center justify-center space-x-2">
            <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
            </svg>
            <span>Analyzing Resume...</span>
          </span>
        ) : (
          "Start Interview"
        )}
      </button>
    </form>
  );
}