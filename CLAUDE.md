# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**Resume-to-Job Intelligence Engine** (use this name in user-facing text; the GitHub repo is still `resume_analyzer_n8n`): an AI resume-to-job matcher. The core design principle: **the LLM only extracts structured evidence; scoring is deterministic code.** Keep that separation when changing matching logic.

The roadmap (core fixes → scalability → local Docker deployment → daily job feed → agents) is in `PLAN.md`. Everything runs locally with Docker Compose; there is no cloud deployment target. Check the plan before starting work and tick items off as they land. Refactors must keep the existing workflow and scoring intact, and changes that alter match scores need explicit approval.

Two generations coexist in this repo, sharing one Postgres database:

- **v1 — n8n workflows** (`Resume_Analyzer.json`, `Job_workflow.json`): import into n8n. Scoring lives in n8n JavaScript Code nodes (60% required / 20% preferred / 20% experience). `README.md` documents only this version.
- **v2 — FastAPI backend (`backend/app/`) + Next.js frontend (`frontend/`)**: the active development path.

## Commands

```bash
# Infrastructure (Postgres with pgvector on :5432, n8n on :5678). Reads .env (copy from .env.example).
docker compose up -d

# Migrations (Alembic, run from backend/; URL comes from app.database / .env)
cd backend && alembic upgrade head
cd backend && alembic revision --autogenerate -m "<message>"   # after changing models
cd backend && alembic check                                     # models == DB?
cd backend && alembic upgrade head --sql > ../schema.sql        # regenerate reference schema

# Backend — run from backend/ (imports are `app.*`), or from anywhere with --app-dir backend
source .venv/bin/activate
cd backend && uvicorn app.main:app --reload    # http://127.0.0.1:8000, docs at /docs

# Frontend
cd frontend && npm run dev     # http://localhost:3000
cd frontend && npm run lint
cd frontend && npm run build
```

There is no test suite. Backend dependencies (direct deps only, pinned): `pip install -r backend/app/requirements.txt` into the repo-root `.venv`.

Backend configuration lives in `backend/app/config.py` (pydantic-settings, `settings` singleton) and is read from env vars and the repo-root `.env`; all options are listed in `.env.example`. Use `settings.*` rather than `os.getenv`. `resumes.file_path` is stored relative to `settings.files_path` (default `<repo>/files`), so the backend works from any working directory. Frontend builds API URLs with `apiUrl()` from `frontend/lib/api.ts` (`NEXT_PUBLIC_API_URL`, inlined at build time).

Databases: one Postgres server (image `pgvector/pgvector:pg16-trixie`, which must stay on trixie/glibc 2.41 to match the stored collation) holds two databases: `n8n` (`POSTGRES_DB`, n8n's internal tables only) and `resume_app` (`APP_DB`, all app tables; also used by the v1 workflows through n8n's "Postgres account" credential). `db/init/` creates `APP_DB` only when the data volume is empty.

## Backend architecture (v2)

Layout: `models/` (SQLAlchemy 2.0 `Mapped` style, shared `Base` in `models/base.py`), `schemas/` (Pydantic), `routers/` (`/api/resumes`, `/api/jobs`, `/api/matches`), `services/` (LLM + matching logic). Schema changes go through Alembic (`backend/migrations/`); a new model module must also be imported in `migrations/env.py`. `jobs` still has v1-only columns (`match_score`, `matched_skills`, …) that the models declare but the v2 code doesn't use.

Matching pipeline — each step is a separate API call and the later ones fail with 404 if earlier ones haven't run:

1. `POST /api/resumes/upload` — PDF → text via pypdf → `resumes` row; original PDF saved to `files/resumes/{id}.pdf`.
2. `POST /api/resumes/{id}/analyze` — `services/resume_analyzer.py` uses OpenAI `responses.parse` with a Pydantic `text_format` → **appends** a new `resume_analyses` row (latest by id wins).
3. `POST /api/jobs/{id}/analyze` — `services/job_analyzer.py`, same pattern → **upserts** the single `job_requirements` row for the job.
4. `POST /api/matches/` `{resume_id, job_id}` — `services/match_engine.calculate_match` → upserts `resume_job_matches` (unique on resume_id+job_id). `matched_skills`/`missing_skills` are stored as JSON strings in TEXT columns.

`match_engine` scoring (sums to 100): required skills 30 + preferred skills 10 (exact match after `normalize_skill`) + semantic similarity 40 (pgvector cosine between resume and job embeddings) + experience 20 (parsed naively from `"N years"` duration strings). Thresholds: ≥80 `APPLY`, ≥60 `CONSIDER`, else `SKIP`.

Embeddings: `services/embedding_service.py` caches vectors (`text-embedding-3-small`, 1536 dims) in the `embeddings` table, unique on `(entity_type, entity_id)`, with a content hash to skip re-embedding; `services/embedding_text.py` builds the text to embed from analysis/requirements. `ensure_resume_embedding` / `ensure_job_embedding` run after each analyze endpoint and again in `POST /api/matches/` (creating missing or stale embeddings, so a match always uses the latest analysis). `services/skill_matcher.py` does per-skill semantic matching via `skill_embeddings` but is not yet wired into `match_engine`.
## Frontend

Next.js 16 App Router, React 19, Tailwind 4. Pages are client components that `fetch(apiUrl("/api/..."))` directly. Backend CORS allows `CORS_ORIGINS` (default `http://localhost:3000`).
