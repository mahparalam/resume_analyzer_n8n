"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";

export default function NewJobPage() {
  const router = useRouter();

  const [company, setCompany] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [jobUrl, setJobUrl] = useState("");
  const [jobDescription, setJobDescription] = useState("");

  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setIsSaving(true);
    setError(null);

    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/jobs/",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            company,
            job_title: jobTitle,
            job_url: jobUrl,
            job_description: jobDescription,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();

        throw new Error(
          errorData.detail ?? "Failed to create job"
        );
      }

      const newJob = await response.json();

      router.push(`/jobs/${newJob.id}`);
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        setError(error.message);
      } else {
        setError("Failed to create job.");
      }
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 px-8 py-10">
      <div className="mx-auto max-w-3xl">

        <Link
          href="/jobs"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          ← Back to Jobs
        </Link>

        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">

          <h1 className="text-2xl font-bold text-gray-900">
            Add Job
          </h1>

          <form
            onSubmit={handleSubmit}
            className="mt-6 space-y-5"
          >

            <div>
              <label
                htmlFor="company"
                className="block text-sm font-medium text-gray-700"
              >
                Company
              </label>

              <input
                id="company"
                type="text"
                value={company}
                onChange={(event) =>
                  setCompany(event.target.value)
                }
                required
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900"
                placeholder="Company name"
              />
            </div>

            <div>
              <label
                htmlFor="jobTitle"
                className="block text-sm font-medium text-gray-700"
              >
                Job Title
              </label>

              <input
                id="jobTitle"
                type="text"
                value={jobTitle}
                onChange={(event) =>
                  setJobTitle(event.target.value)
                }
                required
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900"
                placeholder="AI Engineer"
              />
            </div>

            <div>
              <label
                htmlFor="jobUrl"
                className="block text-sm font-medium text-gray-700"
              >
                Job URL
              </label>

              <input
                id="jobUrl"
                type="url"
                value={jobUrl}
                onChange={(event) =>
                  setJobUrl(event.target.value)
                }
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900"
                placeholder="https://example.com/job"
              />
            </div>

            <div>
              <label
                htmlFor="jobDescription"
                className="block text-sm font-medium text-gray-700"
              >
                Job Description
              </label>

              <textarea
                id="jobDescription"
                value={jobDescription}
                onChange={(event) =>
                  setJobDescription(event.target.value)
                }
                required
                rows={10}
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900"
                placeholder="Paste the job description here..."
              />
            </div>

            {error && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={isSaving}
              className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isSaving ? "Saving..." : "Save Job"}
            </button>

          </form>
        </div>
      </div>
    </main>
  );
}