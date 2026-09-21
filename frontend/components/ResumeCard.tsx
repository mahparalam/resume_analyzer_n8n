"use client";
import { useState } from "react";
type ResumeCardProps = {
  name: string;
  role: string;
};

export default function ResumeCard({
  name,
  role,
}: ResumeCardProps) {
  const [isAnalyzing, setIsAnalyzing] = useState(false);

 const handleAnalyze = async () => {
  setIsAnalyzing(true);

  try {
    const response = await fetch(
      "http://127.0.0.1:8000/api/resumes/4/analyze",
      {
        method: "POST",
      }
    );

    if (!response.ok) {
      throw new Error("Failed to analyze resume");
    }

    const data = await response.json();

    console.log(data);
  } catch (error) {
    console.error(error);
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
            {role}
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
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            {isAnalyzing ? "Analyzing..." : "Analyze with AI"}
          </button>
        </div>

      </div>
    </div>
  );
}