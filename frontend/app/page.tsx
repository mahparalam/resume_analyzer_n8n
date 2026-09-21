"use client";

import { useEffect, useState } from "react";
import ResumeCard from "@/components/ResumeCard";

type Resume = {
  id: number;
  name: string | null;
  email: string | null;
  resume_text: string | null;
};

export default function Home() {
  const [resumes, setResumes] = useState<Resume[]>([]);

  useEffect(() => {
  const fetchResumes = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/resumes/"
      );

      if (!response.ok) {
        throw new Error("Failed to fetch resumes");
      }

      const data = await response.json();

      setResumes(data);
    } catch (error) {
      console.error(error);
    }
  };

  fetchResumes();
}, []);
  return (
    <main className="min-h-screen bg-gray-50 px-8 py-10">
      <div className="mx-auto max-w-6xl">

        <header className="mb-10">
          <h1 className="text-4xl font-bold text-gray-900">
            Resume Intelligence Platform
          </h1>

          <p className="mt-2 text-gray-600">
            Analyze your resume, discover relevant jobs, and understand your
            job matches.
          </p>
        </header>

        <section>
          <div className="mb-5 flex items-center justify-between">
            <h2 className="text-2xl font-semibold text-gray-900">
              Your Resumes
            </h2>

            <button className="rounded-lg bg-black px-5 py-2.5 text-sm font-medium text-white">
              + Upload Resume
            </button>
          </div>

          {resumes.map((resume) => (
          <ResumeCard
            key={resume.id}
            resumeId={resume.id}
            name={resume.name ?? "Unnamed Resume"}
            email={resume.email ?? ""}
          />
        ))}
        </section>

      </div>
    </main>
  );
}