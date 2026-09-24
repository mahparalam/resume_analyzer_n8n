"use client";

import { useEffect, useState } from "react";
import Link from "next/link";

type Resume = {
  id: number;
  name: string | null;
  email: string | null;
  resume_text: string | null;
};

type ExperienceItem = {
  job_title: string;
  company: string;
  duration: string | null;
  responsibilities: string[];
};

type EducationItem = {
  degree: string;
  institution: string;
  duration: string | null;
};

type ProjectItem = {
  name: string;
  technologies: string[];
  description: string;
};

type ResumeAnalysis = {
  id: number;
  resume_id: number;
  summary: string | null;
  skills: string[] | null;
  experience: ExperienceItem[] | null;
  education: EducationItem[] | null;
  projects: ProjectItem[] | null;
};

export default function ResumePage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const [resumeId, setResumeId] = useState<string | null>(null);
  const [resume, setResume] = useState<Resume | null>(null);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);

  const [isLoading, setIsLoading] = useState(true);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const [error, setError] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  useEffect(() => {
    const loadResume = async () => {
      try {
        const { id } = await params;
        setResumeId(id);

        const resumeResponse = await fetch(
          `http://127.0.0.1:8000/api/resumes/${id}`
        );

        if (!resumeResponse.ok) {
          throw new Error("Failed to fetch resume");
        }

        const resumeData = await resumeResponse.json();
        setResume(resumeData);

        const analysisResponse = await fetch(
          `http://127.0.0.1:8000/api/resumes/${id}/analysis`
        );

        if (analysisResponse.ok) {
          const analysisData = await analysisResponse.json();
          setAnalysis(analysisData);
        }
      } catch (error) {
        console.error(error);
        setError("Failed to load resume.");
      } finally {
        setIsLoading(false);
      }
    };

    loadResume();
  }, [params]);

  const handleAnalyze = async () => {
    if (!resumeId) {
      return;
    }

    setIsAnalyzing(true);
    setAnalysisError(null);

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

      setAnalysis({
        id: data.id ?? 0,
        resume_id: Number(resumeId),
        ...data.analysis,
      });
    } catch (error) {
      console.error(error);
      setAnalysisError(
        "Failed to analyze resume. Please try again."
      );
    } finally {
      setIsAnalyzing(false);
    }
  };

  if (isLoading) {
    return (
      <main className="min-h-screen bg-gray-50 px-8 py-10">
        <div className="mx-auto max-w-5xl">
          <p className="text-gray-600">Loading resume...</p>
        </div>
      </main>
    );
  }

  if (error || !resume) {
    return (
      <main className="min-h-screen bg-gray-50 px-8 py-10">
        <div className="mx-auto max-w-5xl">
          <p className="text-red-600">
            {error ?? "Resume not found."}
          </p>

          <Link
            href="/"
            className="mt-4 inline-block text-blue-600 hover:underline"
          >
            ← Back to Resumes
          </Link>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-gray-50 px-8 py-10">
      <div className="mx-auto max-w-5xl">

        {/* Back button */}
        <Link
          href="/"
          className="text-sm font-medium text-blue-600 hover:underline"
        >
          ← Back to Resumes
        </Link>

        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
            <h1 className="text-3xl font-bold text-gray-900">
              {resume.name ?? "Unnamed Resume"}
            </h1>
            {resume.email && (
              <p className="mt-2 text-gray-600">
                {resume.email}
              </p>
            )}

            <a
              href={`http://127.0.0.1:8000/api/resumes/${resumeId}/file`}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-4 inline-block rounded-lg bg-gray-900 px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
            >
              View Original Resume
            </a>
          </div>

        {/* AI analysis */}
        <div className="mt-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
          <div className="flex items-center justify-between gap-4">
            <h2 className="text-xl font-semibold text-gray-900">
              AI Analysis
            </h2>

            <button
              onClick={handleAnalyze}
              disabled={isAnalyzing}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isAnalyzing ? "Analyzing..." : "Analyze with AI"}
            </button>
          </div>

          {analysisError && (
            <div className="mt-4 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
              {analysisError}
            </div>
          )}

          {!analysis && !isAnalyzing && !analysisError && (
            <p className="mt-6 text-gray-600">
              This resume has not been analyzed yet.
            </p>
          )}

          {analysis && (
            <div className="mt-6 space-y-8">

              {/* Summary */}
              {analysis.summary && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-900">
                    Summary
                  </h3>

                  <p className="mt-2 leading-7 text-gray-700">
                    {analysis.summary}
                  </p>
                </section>
              )}

              {/* Skills */}
              {analysis.skills && analysis.skills.length > 0 && (
                <section>
                  <h3 className="text-lg font-semibold text-gray-900">
                    Skills
                  </h3>

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
                </section>
              )}

              {/* Experience */}
              {analysis.experience &&
                analysis.experience.length > 0 && (
                  <section>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Experience
                    </h3>

                    <div className="mt-4 space-y-5">
                      {analysis.experience.map((item, index) => (
                        <div
                          key={`${item.company}-${item.job_title}-${index}`}
                          className="border-l-2 border-gray-200 pl-4"
                        >
                          <h4 className="font-semibold text-gray-900">
                            {item.job_title}
                          </h4>

                          <p className="text-gray-700">
                            {item.company}
                          </p>

                          {item.duration && (
                            <p className="text-sm text-gray-500">
                              {item.duration}
                            </p>
                          )}

                          {item.responsibilities.length > 0 && (
                            <ul className="mt-2 list-disc space-y-1 pl-5 text-gray-700">
                              {item.responsibilities.map(
                                (responsibility, responsibilityIndex) => (
                                  <li key={responsibilityIndex}>
                                    {responsibility}
                                  </li>
                                )
                              )}
                            </ul>
                          )}
                        </div>
                      ))}
                    </div>
                  </section>
                )}

              {/* Education */}
              {analysis.education &&
                analysis.education.length > 0 && (
                  <section>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Education
                    </h3>

                    <div className="mt-4 space-y-4">
                      {analysis.education.map((item, index) => (
                        <div
                          key={`${item.institution}-${item.degree}-${index}`}
                        >
                          <h4 className="font-semibold text-gray-900">
                            {item.degree}
                          </h4>

                          <p className="text-gray-700">
                            {item.institution}
                          </p>

                          {item.duration && (
                            <p className="text-sm text-gray-500">
                              {item.duration}
                            </p>
                          )}
                        </div>
                      ))}
                    </div>
                  </section>
                )}

              {/* Projects */}
              {analysis.projects &&
                analysis.projects.length > 0 && (
                  <section>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Projects
                    </h3>

                    <div className="mt-4 space-y-5">
                      {analysis.projects.map((project, index) => (
                        <div
                          key={`${project.name}-${index}`}
                          className="rounded-lg border border-gray-200 p-4"
                        >
                          <h4 className="font-semibold text-gray-900">
                            {project.name}
                          </h4>

                          {project.technologies.length > 0 && (
                            <p className="mt-1 text-sm text-gray-500">
                              {project.technologies.join(", ")}
                            </p>
                          )}

                          <p className="mt-2 leading-6 text-gray-700">
                            {project.description}
                          </p>
                        </div>
                      ))}
                    </div>
                  </section>
                )}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}