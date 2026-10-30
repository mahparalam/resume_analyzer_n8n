// Base URL of the FastAPI backend. NEXT_PUBLIC_ variables are inlined at
// build time, so changing it requires restarting `next dev` or rebuilding.
export const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000"
).replace(/\/+$/, "");

export function apiUrl(path: string): string {
  return `${API_BASE_URL}${path.startsWith("/") ? path : `/${path}`}`;
}
