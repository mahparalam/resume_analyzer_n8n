import Link from "next/link";

type JobCardProps = {
  jobId: number;
  company: string | null;
  jobTitle: string | null;
  jobUrl: string | null;
};

export default function JobCard({
  jobId,
  company,
  jobTitle,
  jobUrl,
}: JobCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-gray-900">
        {jobTitle ?? "Untitled Job"}
      </h2>

      <p className="mt-2 text-gray-600">
        {company ?? "Unknown Company"}
      </p>

      <div className="mt-4 flex gap-3">
        <Link
          href={`/jobs/${jobId}`}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          View Job
        </Link>

        {jobUrl && (
          <a
            href={jobUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            Job Posting
          </a>
        )}
      </div>
    </div>
  );
}