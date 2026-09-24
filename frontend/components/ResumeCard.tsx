import Link from "next/link";

type ResumeCardProps = {
  resumeId: number;
  name: string;
  email: string;
};

export default function ResumeCard({
  resumeId,
  name,
  email,
}: ResumeCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-6 shadow-sm">
      <h2 className="text-xl font-semibold text-gray-900">
        {name}
      </h2>

      <p className="mt-2 text-gray-600">
        {email}
      </p>

      <div className="mt-4">
        <Link
          href={`/resumes/${resumeId}`}
          className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
        >
          View Resume
        </Link>
      </div>
    </div>
  );
}