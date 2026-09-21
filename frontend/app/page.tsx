import ResumeCard from "@/components/ResumeCard";

export default function Home() {
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

          <ResumeCard
            name="Mahpara Yasmin"
            role="AI Engineer"
          />
        </section>

      </div>
    </main>
  );
}