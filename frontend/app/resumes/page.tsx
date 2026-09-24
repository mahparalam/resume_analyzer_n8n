"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import ResumeCard from "@/components/ResumeCard";

type Resume = {
  id: number;
  name: string | null;
  email: string | null;
  resume_text: string | null;
};

export default function ResumesPage() {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
        setError("Failed to load resumes.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchResumes();
  }, []);

  return (
    <main className="min-h-screen bg-gray-50 px-8 py-10">
        <Link
        href="/"
        className="mb-4 inline-block text-sm text-gray-600 hover:text-gray-900"
        >
        ← Back to Home
        </Link>
      <div className="mx-auto max-w-6xl">

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Resumes
            </h1>

            <p className="mt-2 text-gray-600">
              Manage and analyze candidate resumes
            </p>
          </div>

          <Link
            href="/resumes/new"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            + Add Resume
          </Link>
        </div>

        {isLoading && (
          <p className="mt-8 text-gray-600">
            Loading resumes...
          </p>
        )}

        {error && (
          <p className="mt-8 text-red-600">
            {error}
          </p>
        )}

        {!isLoading && !error && resumes.length === 0 && (
          <p className="mt-8 text-gray-600">
            No resumes found.
          </p>
        )}

        <div className="mt-8 grid gap-6">
          {resumes.map((resume) => (
            <ResumeCard
              key={resume.id}
              resumeId={resume.id}
              name={resume.name ?? "Unnamed Resume"}
              email={resume.email ?? ""}
            />
          ))}
        </div>

      </div>
    </main>
  );
}