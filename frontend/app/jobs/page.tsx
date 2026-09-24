"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import JobCard from "@/components/JobCard";

type Job = {
  id: number;
  company: string | null;
  job_title: string | null;
  job_url: string | null;
  job_description: string | null;
  match_score: number | null;
  matched_skills: string | null;
};

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const response = await fetch(
          "http://127.0.0.1:8000/api/jobs/"
        );

        if (!response.ok) {
          throw new Error("Failed to fetch jobs");
        }

        const data = await response.json();
        setJobs(data);
      } catch (error) {
        console.error(error);
        setError("Failed to load jobs.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchJobs();
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
              Job Intelligence
            </h1>

            <p className="mt-2 text-gray-600">
              Manage and explore job opportunities
            </p>
          </div>

          <Link
            href="/jobs/new"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            + Add Job
          </Link>
        </div>

        {isLoading && (
          <p className="mt-8 text-gray-600">
            Loading jobs...
          </p>
        )}

        {error && (
          <p className="mt-8 text-red-600">
            {error}
          </p>
        )}

        {!isLoading && !error && jobs.length === 0 && (
          <p className="mt-8 text-gray-600">
            No jobs found.
          </p>
        )}

        <div className="mt-8 grid gap-6">
          {jobs.map((job) => (
            <JobCard
              key={job.id}
              jobId={job.id}
              company={job.company}
              jobTitle={job.job_title}
              jobUrl={job.job_url}
            />
          ))}
        </div>

      </div>
    </main>
  );
}