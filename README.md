# Resume-to-Job Intelligence Engine

An AI-powered engine that matches resumes to job openings. It reads a PDF resume and a job description, extracts structured evidence from both with an LLM, and calculates an explainable match score with an **APPLY / CONSIDER / SKIP** recommendation.

Built with **FastAPI, PostgreSQL + pgvector, OpenAI, Next.js and Docker**. The original n8n workflows (v1) are still included.

## Core Idea

The LLM never decides whether a candidate is a good fit. It only **extracts evidence**: skills, experience, education, projects, and the job's required and preferred skills. The **score is calculated by deterministic code** from that evidence, so results are consistent, explainable and easy to tune without changing prompts.

## Current Status

| Area | Status |
|---|---|
| Resume upload (PDF → text, original file stored) | Done |
| AI resume analysis (summary, skills, experience, education, projects) | Done |
| Job management and AI job analysis (required/preferred skills, years, education, responsibilities) | Done |
| Semantic similarity with OpenAI embeddings stored in pgvector | Done |
| Deterministic match scoring and recommendation | Done |
| Database migrations (Alembic) and a dedicated application database | Done |
| Central configuration through environment variables | Done |
| Web UI: resumes (list, upload, view, analyze) and jobs (list, add, view) | Done |
| Web UI for job analysis and matching | Not yet (available through the API) |
| Automated tests | Not yet |
| v1 n8n workflows | Included; their future role is under review |

## Architecture

```text
              Next.js frontend (localhost:3000)
                          │  REST
                          ▼
               FastAPI backend (localhost:8000)
     ┌────────────┬───────┴──────┬─────────────────┐
     ▼            ▼              ▼                 ▼
 Resume PDF   OpenAI LLM     OpenAI embeddings   Match engine
 (pypdf)      structured     text-embedding-     (deterministic
              extraction     3-small             scoring)
     │            │              │                 │
     └────────────┴──────┬───────┴─────────────────┘
                         ▼
         PostgreSQL 16 + pgvector  (database: resume_app)
```

### Matching Pipeline

Each step is a separate API call:

1. **Upload a resume** (`POST /api/resumes/upload`). Text is extracted with pypdf, and the original PDF is saved under `files/resumes/`.
2. **Analyze the resume** (`POST /api/resumes/{id}/analyze`). The LLM returns structured data (summary, skills, experience, education, projects), validated against a Pydantic schema. An embedding of the analysis is stored.
3. **Add and analyze a job** (`POST /api/jobs/`, then `POST /api/jobs/{id}/analyze`). The LLM extracts required and preferred skills, years of experience, education and responsibilities. An embedding is stored.
4. **Match** (`POST /api/matches/` with `{"resume_id": …, "job_id": …}`). Missing or outdated embeddings are created automatically, the score is calculated, and the result is saved. Re-running a match updates the existing result.

Embeddings are cached with a content hash, so unchanged resumes and jobs are never re-embedded.

## Matching Logic

The score is out of 100:

| Component | Points | How it's calculated |
|---|---|---|
| Required skills | 30 | Share of the job's required skills found in the resume |
| Preferred skills | 10 | Share of the job's preferred skills found in the resume |
| Semantic similarity | 40 | Cosine similarity between the resume and job embeddings × 40 |
| Experience | 20 | Resume years compared with the job's required years (below) |

Skills are compared after normalization (lowercase, punctuation and extra spaces removed).

| Experience match | Condition | Points |
|---|---|---|
| Strong | ≥ required years | 20 |
| Good | ≥ 70% of required years | 15 |
| Partial | ≥ 50% of required years | 10 |
| Weak | below 50% | 5 |
| Not specified | the job states no required years | 10 |

| Score | Recommendation |
|---|---|
| 80–100 | APPLY |
| 60–79 | CONSIDER |
| 0–59 | SKIP |

Each match result also lists the matched and missing skills, the experience match and the raw semantic similarity, so every score can be explained.

## API

Interactive documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs) while the backend is running.

| Method | Endpoint | Purpose |
|---|---|---|
| `POST` | `/api/resumes/upload` | Upload a PDF resume (`file`, `name`, `email`) |
| `GET` | `/api/resumes/` · `/api/resumes/{id}` | List or get resumes |
| `PUT` · `DELETE` | `/api/resumes/{id}` | Update or delete a resume |
| `POST` | `/api/resumes/{id}/analyze` | Run AI analysis on a resume |
| `GET` | `/api/resumes/{id}/analysis` | Latest analysis for a resume |
| `GET` | `/api/resumes/{id}/file` | Download the original PDF |
| `POST` | `/api/jobs/` | Create a job |
| `GET` | `/api/jobs/` · `/api/jobs/{id}` | List or get jobs |
| `PUT` · `DELETE` | `/api/jobs/{id}` | Update or delete a job |
| `POST` | `/api/jobs/{id}/analyze` | Run AI analysis on a job description |
| `GET` | `/api/jobs/{id}/requirements` | Extracted job requirements |
| `POST` | `/api/matches/` | Score a resume against a job |

## Tech Stack

| Layer | Tools |
|---|---|
| Backend API | FastAPI, Pydantic, pydantic-settings |
| Database | PostgreSQL 16, pgvector, SQLAlchemy 2.0, Alembic |
| AI | OpenAI structured outputs (`gpt-5.6-luna` by default), `text-embedding-3-small` embeddings |
| Documents | pypdf |
| Frontend | Next.js 16 (App Router), React 19, Tailwind CSS 4, TypeScript |
| Infrastructure | Docker Compose |
| Workflow automation (v1) | n8n |

## Database

All application tables live in their own database, `resume_app` (set with `APP_DB`), separate from n8n's internal database. The schema is managed with Alembic; [`schema.sql`](./schema.sql) is generated from the migrations for reference.

| Table | Contents |
|---|---|
| `resumes` | Candidate name, email, extracted text, path of the stored PDF |
| `resume_analyses` | AI analysis of a resume (summary, skills, experience, education, projects as JSONB) |
| `jobs` | Company, title, URL (unique), description |
| `job_requirements` | AI-extracted requirements of a job (JSONB) |
| `resume_job_matches` | Score, matched/missing skills, experience match and recommendation; unique per resume and job |
| `embeddings` | One vector per resume or job, with a content hash for caching |
| `skill_embeddings` | One vector per normalized skill, for semantic skill matching |

## Running Locally

### Prerequisites

- Docker and Docker Compose
- Python 3.12+
- Node.js 20+
- An OpenAI API key

### 1. Clone and configure

```bash
git clone https://github.com/mahparalam/resume_analyzer_n8n.git
cd resume_analyzer_n8n
cp .env.example .env
```

Edit `.env` and set at least `POSTGRES_PASSWORD` and `OPENAI_API_KEY`. **Never commit `.env`.**

### 2. Start PostgreSQL (and n8n)

```bash
docker compose up -d
```

On the first start, the `resume_app` database is created automatically.

### 3. Set up the backend

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r backend/app/requirements.txt

cd backend
alembic upgrade head                  # create or update the tables
uvicorn app.main:app --reload         # http://127.0.0.1:8000
```

### 4. Start the frontend

```bash
cd frontend
npm install
npm run dev                           # http://localhost:3000
```

To use a different backend URL, copy `frontend/.env.example` to `frontend/.env.local` and set `NEXT_PUBLIC_API_URL`.

### Configuration

All backend settings are read from environment variables or the repo-root `.env`. Optional settings and their defaults are listed in [`.env.example`](./.env.example).

| Variable | Default | Purpose |
|---|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` | — | Database credentials |
| `APP_DB` | `resume_app` | Application database name |
| `POSTGRES_HOST` / `POSTGRES_PORT` | `localhost` / `5432` | Database location |
| `DATABASE_URL` | — | Full connection URL; overrides the settings above |
| `OPENAI_API_KEY` | — | OpenAI API key |
| `OPENAI_MODEL` | `gpt-5.6-luna` | Model used for resume and job analysis |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | Embedding model |
| `FILES_DIR` | `files` | Where uploaded PDFs are stored (relative to the repo root) |
| `CORS_ORIGINS` | `http://localhost:3000` | Comma-separated origins allowed to call the API |

## Project Structure

```text
resume_analyzer_n8n/
├── backend/
│   ├── alembic.ini
│   ├── migrations/            # Alembic migrations
│   └── app/
│       ├── main.py            # FastAPI app
│       ├── config.py          # settings from environment variables
│       ├── database.py
│       ├── models/            # SQLAlchemy models
│       ├── schemas/           # Pydantic request/response and LLM output schemas
│       ├── routers/           # /api/resumes, /api/jobs, /api/matches
│       └── services/          # LLM analysis, embeddings, match engine
├── frontend/                  # Next.js app (app/, components/, lib/api.ts)
├── db/init/                   # creates the application database on first start
├── compose.yaml               # PostgreSQL + pgvector, n8n
├── schema.sql                 # generated from the migrations
├── Resume_Analyzer.json       # v1 n8n workflow
├── Job_workflow.json          # v1 n8n workflow
└── .env.example
```

Uploaded resumes (`files/`), `.env` and other local files are excluded through `.gitignore`.

## v1: n8n Workflows

The first version of the project ran entirely in n8n. The workflows are still included, and their future role is under review.

- **Resume Analyzer** (`Resume_Analyzer.json`): Manual Trigger → Read File → Extract PDF → OpenAI → Parse → insert into `resumes`
- **Job Workflow** (`Job_workflow.json`): Webhook → Upsert Job → Get Resume → OpenAI Matcher → Deterministic Scoring → Upsert Match

v1 uses its own scoring (60% required skills, 20% preferred skills, 20% experience) and the same Apply / Consider / Skip thresholds.

To use them, open n8n at [http://localhost:5678](http://localhost:5678), create PostgreSQL and OpenAI credentials, and import both JSON files. Point the PostgreSQL credential at the application database (`resume_app`). Example request once the Job Workflow is active in test mode:

```bash
curl -X POST http://localhost:5678/webhook-test/job \
  -H "Content-Type: application/json" \
  -d '{
    "resume_id": 1,
    "company": "Example Company",
    "job_title": "AI Engineer",
    "job_url": "https://example.com/job/123",
    "job_description": "Looking for an AI Engineer with Python, LLM, RAG and Docker experience."
  }'
```

## Known Limitations

- Experience is read only from durations written as "N years". Date ranges such as "Aug 2024 – Present" count as zero.
- Analyzing a resume again adds a new analysis row instead of replacing the previous one; the latest is used.
- Creating a job with a URL that already exists returns an error instead of updating the job.
- OpenAI errors and timeouts surface as generic server errors.
- No authentication; the app is intended for local use.
- Resumes created before PDF storage was added have no original file to download.

## Future Work and Improvements

### Core fixes
- **Experience parsing:** read date ranges (including "Present"), calculate experience in years and months, and count overlapping jobs only once
- **One analysis per resume:** keep only the latest analysis
- **Job upsert by URL** so the same posting can be submitted again safely
- **Clearer errors** for OpenAI failures and PDFs without extractable text
- **Resume file handling:** hide "View Original Resume" when no file is stored
- **Automated tests:** unit tests for the scoring rules and API tests with OpenAI mocked

### Scalability
- **Background jobs:** move LLM and embedding calls to a worker queue (Redis) so requests return immediately
- **Batch embeddings** for skills instead of one request per skill
- **Vector indexes** (HNSW) for fast similarity search
- **One-to-many matching:** rank one resume against many jobs, using vector search to shortlist before scoring
- **Pagination** on list endpoints, structured logging and a health endpoint

### Full local Docker deployment
- Dockerfiles for the backend, worker and frontend
- One command to start the whole stack (`docker compose up -d --build`), with health checks, migrations on start-up, persistent volumes and a backup script

### Daily job feed and notifications
- Fetch new job openings every day from official job APIs and feeds, then analyze and match them automatically
- Daily email digest of new APPLY / CONSIDER jobs at a time each user chooses on the website
- "New today" badges, filters and match results on the jobs page
- User accounts and notification settings

### AI agents and smart features
- **Career-page scraper agent** for companies without a job API, running generated code in a disposable, locked-down container
- **Duplicate job detection** across job boards using embeddings
- **Weekly skill-gap trends:** the skills that appear most often in jobs you're missing
- **Resume tailoring suggestions** for strong matches, based only on evidence already in the resume
- **Feedback signals:** "Applied" / "Not interested" to filter future suggestions
- **Match explanations** written for recruiters
- **Evaluation set** of fixed resume/job pairs to catch regressions when prompts or models change
