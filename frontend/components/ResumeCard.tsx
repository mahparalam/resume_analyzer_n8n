"use client";
import { useState } from "react";

type ResumeAnalysis = {
  summary: string;
  skills: string[];
  experience: {
    job_title: string;
    company: string;
    duration: string | null;
    responsibilities: string[];
  }[];
  education: {
    degree: string;
    institution: string;
    duration: string | null;
  }[];
  projects: {
    name: string;
    technologies: string[];
    description: string;
  }[];
};

type ResumeCardProps = {
  resumeId: number;
  name: string;
  email: string;
};

export default function ResumeCard({
  resumeId,
  name,
  email,
}: ResumeCardProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleAnalyze = async () => {
  setIsAnalyzing(true);
  setError(null);

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/api/resumes/${resumeId}/analyze`,
      {
        method: "POST",
      }
    );

    if (!response.ok) {
      throw new Error("Failed to analyze resume");
    }

    const data = await response.json();

    setAnalysis(data.analysis);
  } catch (error) {
    console.error(error);
    setError("Failed to analyze resume. Please try again.");
  } finally {
    setIsAnalyzing(false);
  }
};

  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <div className="flex items-center justify-between">

        <div>
          <h3 className="text-xl font-semibold text-gray-900">
            {name}
          </h3>

          <p className="mt-1 text-gray-600">
            {email}
          </p>

          <p className="mt-2 text-sm text-gray-500">
            Resume uploaded
          </p>
        </div>

        <div className="flex gap-3">
          <button className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50">
            View Resume
          </button>

          <button
            onClick={handleAnalyze}
            disabled={isAnalyzing}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {isAnalyzing ? "Analyzing..." : "Analyze with AI"}
          </button>
        </div>

      </div>
      {error && (
        <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
          {error}
        </div>
      )}
      {/* AI Analysis */}
      {analysis && (
      <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 text-gray-900 shadow-sm">

        <h3 className="text-2xl font-semibold text-gray-900">
          AI Resume Analysis
        </h3>

        {/* Summary */}
        <div className="mt-6">
          <h4 className="text-lg font-semibold text-gray-900">
            Summary
          </h4>

          <p className="mt-2 leading-7 text-gray-700">
            {analysis.summary}
          </p>
        </div>

        {/* Skills */}
        <div className="mt-6">
          <h4 className="text-lg font-semibold text-gray-900">
            Skills
          </h4>

          <div className="mt-3 flex flex-wrap gap-2">
            {analysis.skills.map((skill, index) => (
              <span
                key={`${skill}-${index}`}
                className="rounded-full bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800"
              >
                {skill}
              </span>
            ))}
          </div>
        </div>

      </div>
    )}
    </div>
  );
}