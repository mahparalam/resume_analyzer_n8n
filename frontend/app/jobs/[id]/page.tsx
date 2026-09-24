"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type Job = {
  id: number;
  company: string | null;
  job_title: string | null;
  job_url: string | null;
  job_description: string | null;
  match_score: number | null;
  matched_skills: string | null;
};

export default function JobDetailsPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [job, setJob] = useState<Job | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJob = async () => {
      try {
        const { id } = await params;

        const response = await fetch(
          `http://127.0.0.1:8000/api/jobs/${id}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch job");
        }

        const data = await response.json();
        setJob(data);
      } catch (error) {
        console.error(error);
        setError("Failed to load job.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchJob();
  }, [params]);

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 px-8 py-10">
        <div className="mx-auto max-w-5xl">
          <p className="text-gray-600">Loading job...</p>
        </div>
      </main>
    );
  }

  if (error || !job) {
    return (
      <main className="min-h-screen bg-gray-50 px-8 py-10">
        <div className="mx-auto max-w-5xl">
          <p className="text-red-600">
            {error ?? "Job not found."}
          </p>

          <Link
            href="/jobs"
            className="mt-4 inline-block text-blue-600 hover:underline"
          >
            ← Back to Jobs
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 px-8 py-10">
      <div className="mx-auto max-w-5xl">

        <Link
          href="/jobs"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          ← Back to Jobs
        </Link>

        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h1 className="text-3xl font-bold text-gray-900">
            {job.job_title ?? "Untitled Job"}
          </h1>

          <p className="mt-2 text-lg text-gray-600">
            {job.company ?? "Unknown Company"}
          </p>

          {job.job_url && (
            <a
              href={job.job_url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-block text-blue-600 hover:underline"
            >
              View Job Posting →
            </a>
          )}
        </div>

        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-900">
            Job Description
          </h2>

          <div className="mt-4 whitespace-pre-wrap leading-7 text-gray-700">
            {job.job_description ?? "No job description available."}
          </div>
        </div>

        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-900">
            Resume Matching
          </h2>

          <p className="mt-2 text-gray-600">
            Resume matching will be available in the next milestone.
          </p>
        </div>

      </div>
    </main>
  );
}