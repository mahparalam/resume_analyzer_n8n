import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50 px-8 py-10">
      <div className="mx-auto max-w-6xl">

        <h1 className="text-3xl font-bold text-gray-900">
          Resume Intelligence Platform
        </h1>

        <p className="mt-2 text-gray-600">
          Manage resumes and jobs, then match candidates with opportunities.
        </p>

        <div className="mt-8 grid gap-6 md:grid-cols-2">

          <Link
            href="/resumes"
            className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md"
          >
            <h2 className="text-xl font-semibold text-gray-900">
              Resumes
            </h2>

            <p className="mt-2 text-gray-600">
              Upload, manage, analyze, and view resumes.
            </p>
          </Link>

          <Link
            href="/jobs"
            className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm hover:shadow-md"
          >
            <h2 className="text-xl font-semibold text-gray-900">
              Jobs
            </h2>

            <p className="mt-2 text-gray-600">
              Manage job opportunities and job descriptions.
            </p>
          </Link>

        </div>

      </div>
    </main>
  );
}