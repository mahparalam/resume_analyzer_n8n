"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import ResumeCard from "@/components/ResumeCard";

type Resume = {
  id: number;
  name: string | null;
  email: string | null;
  resume_text: string | null;
};

export default function Home() {
  const router = useRouter();

  const [resumes, setResumes] = useState<Resume[]>([]);

  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [file, setFile] = useState<File | null>(null);

  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);

  useEffect(() => {
    fetchResumes();
  }, []);

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

  const handleFileChange = (
    event: React.ChangeEvent<HTMLInputElement>
  ) => {
    const selectedFile = event.target.files?.[0] ?? null;
    setFile(selectedFile);
  };

  const handleUpload = async (
    event: React.FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    if (!file) {
      setUploadError("Please select a PDF file.");
      return;
    }

    if (file.type !== "application/pdf") {
      setUploadError("Only PDF files are allowed.");
      return;
    }

    setIsUploading(true);
    setUploadError(null);

    try {
      const formData = new FormData();

      formData.append("file", file);
      formData.append("name", name);
      formData.append("email", email);

      const response = await fetch(
        "http://127.0.0.1:8000/api/resumes/upload",
        {
          method: "POST",
          body: formData,
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail ?? "Failed to upload resume"
        );
      }

      const newResume = await response.json();

      // Go directly to the newly uploaded resume
      router.push(`/resumes/${newResume.id}`);
    } catch (error) {
      console.error(error);

      if (error instanceof Error) {
        setUploadError(error.message);
      } else {
        setUploadError("Failed to upload resume.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 px-8 py-10">
      <div className="mx-auto max-w-6xl">

        <h1 className="text-3xl font-bold text-gray-900">
          Resume Intelligence Platform
        </h1>

        <p className="mt-2 text-gray-600">
          Upload and manage your resumes
        </p>

        {/* Upload Resume */}
        <div className="mt-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold text-gray-900">
            Add Resume
          </h2>

          <form
            onSubmit={handleUpload}
            className="mt-6 space-y-4"
          >
            <div>
              <label
                htmlFor="name"
                className="block text-sm font-medium text-gray-700"
              >
                Name
              </label>

              <input
                id="name"
                type="text"
                value={name}
                onChange={(event) => setName(event.target.value)}
                required
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 outline-none focus:border-blue-500"
                placeholder="Enter candidate name"
              />
            </div>

            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700"
              >
                Email
              </label>

              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                required
                className="mt-1 w-full rounded-lg border border-gray-300 px-3 py-2 text-gray-900 outline-none focus:border-blue-500"
                placeholder="Enter email"
              />
            </div>

            <div>
              <label
                htmlFor="resume"
                className="block text-sm font-medium text-gray-700"
              >
                Resume PDF
              </label>

              <input
                id="resume"
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                required
                className="mt-1 block w-full text-sm text-gray-700"
              />
            </div>

            {uploadError && (
              <div className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm text-red-700">
                {uploadError}
              </div>
            )}

            <button
              type="submit"
              disabled={isUploading}
              className="rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isUploading ? "Uploading..." : "Upload Resume"}
            </button>
          </form>
        </div>

        {/* Resume List */}
        <div className="mt-10">
          <h2 className="text-xl font-semibold text-gray-900">
            Resumes
          </h2>

          <div className="mt-5 grid gap-6">
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

      </div>
    </main>
  );
}