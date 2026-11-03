# Project Plan — Resume-to-Job Intelligence Engine

**Goal:** make the project scalable and run the whole stack locally with Docker Compose, adding agents where they genuinely help.

**Constraint:** keep the existing workflow and logic intact:
- The flow stays: upload → analyze resume → analyze job → match.
- The LLM extracts evidence only. Scoring stays deterministic in `match_engine.py` (30 required / 10 preferred / 40 semantic / 20 experience; APPLY ≥80, CONSIDER ≥60).
- The v1 n8n workflows (`Resume_Analyzer.json`, `Job_workflow.json`) keep working.
- Any change that would alter scores is called out and approved separately.

**Decisions (2026-10-28):**
- Everything runs **locally on Docker** (Docker Compose); there is no cloud deployment target. (Changed 2026-10-30: an earlier plan to use the E2B cloud sandbox was dropped.)
- Resume analysis keeps **only the latest** analysis per resume (upsert, no history).
- Experience parsing fix **approved**: map "Present" to the current date and calculate experience in years and months.
- v1 n8n workflows **stay as they are**. Later, a scheduled job will fetch openings daily, email the user, and update the job listing on the portal. Whether that runs in n8n is **undecided** (see open question 3).
- Overlapping jobs **count once**: merge date intervals before summing.
- Email goes through **Gmail** at each user's **preferred time**, which they choose on the website.
- **All the new ideas are approved** (see Phase 5).
- Job sources, locations and keywords: **decide together when building Phase 4**.

Status legend: `[ ]` todo · `[~]` in progress · `[x]` done

---

## Phase 0 — Repo hygiene (no behavior change)

- [x] Add `__pycache__/`, `*.pyc`, `.venv/` to `.gitignore`; `git rm -r --cached` the tracked `.pyc` files. Also fixed `.gitignore`, which had the literal heredoc command saved as its first line.
- [x] Move `services/letter.py` out of the app; it now lives outside the repository
- [x] Complete `backend/app/requirements.txt` with pinned direct dependencies; removed the root `requirements.txt` (a freeze of the system Python)
- [x] Commit the in-progress pgvector work (compose image switch, embedding models/services, `match_engine` changes). Matching still returns 500 until 1.1 lands.
- [x] Commit Next.js-generated `frontend/AGENTS.md` / `frontend/CLAUDE.md`

## Phase 1 — Fix the core implementation

**1.1 Embeddings wiring (currently breaks matching)**
- [x] After `POST /resumes/{id}/analyze`, build text via `build_resume_embedding_text` and call `get_or_create_embedding(entity_type="resume")`
- [x] Same for `POST /jobs/{id}/analyze` with `build_job_embedding_text` (`entity_type="job"`)
- [x] In `POST /matches/`, lazily create missing embeddings instead of returning 500 (also refreshes stale ones; 422 if there's nothing to embed)
- [x] Add unique constraint on `embeddings(entity_type, entity_id)` (already in the DB; now declared in the model)

**1.2 Schema and migrations**
- [x] Introduce Alembic (`backend/alembic.ini`, `backend/migrations/`); baseline `df775c301f09` is identical to the original tables (verified with a `pg_dump -s` diff and `alembic check`)
- [x] Migration includes `CREATE EXTENSION vector`, `resumes.file_path`, `embeddings`, `skill_embeddings`
- [x] App tables moved to a separate `resume_app` database (`APP_DB`); data copied and verified (row checksums + sequences). Fresh installs get the DB from `db/init/01-create-app-db.sh`
- [ ] **On hold (n8n decision pending):** repoint the n8n "Postgres account" credential to `resume_app`. It still points at `n8n`, so v1 workflows use the old tables until then
- [ ] **On hold (n8n decision pending):** drop the old app tables from the `n8n` database once v1 is confirmed working on `resume_app` (needs approval). A full `pg_dumpall` backup was taken before the move
- [x] `schema.sql` regenerated from migrations (`alembic upgrade head --sql`)
- [x] Collation warning fixed: image `pgvector/pgvector:pg16-trixie` (glibc 2.41 matches the data) and all databases reindexed

**1.3 Configuration**
- [x] Central settings (`backend/app/config.py`, pydantic-settings): `DATABASE_URL` or `POSTGRES_HOST/PORT/USER/PASSWORD` + `APP_DB`, `OPENAI_API_KEY`, `OPENAI_MODEL`, `EMBEDDING_MODEL`, `FILES_DIR`, `CORS_ORIGINS`
- [x] Replace the hardcoded `localhost:5432` and the cwd-relative `../files/resumes`. `resumes.file_path` is now relative to `FILES_DIR` (migration `ed0f70a867de`)
- [x] Frontend: `NEXT_PUBLIC_API_URL` via `frontend/lib/api.ts` (`apiUrl()`) instead of hardcoded `127.0.0.1:8000` in each page
- [ ] Pre-existing lint error: unescaped `'` in `frontend/app/resumes/new/page.tsx:100`

**1.4 Resume file handling**
- [x] Expose `has_file` in `ResumeResponse` (checks the file really exists); hide "View Original Resume" when there is no file
- [x] Backfill resume 1 from `files/resume.pdf`: copied to `files/resumes/1.pdf`, `file_path` set. Text verified identical apart from bullet characters
- [~] Backfill resumes 4, 5 and 6 from `files/resume.pdf` (approved 2026-11-03; their text matches exactly). Waiting for Postgres to be running. Note: resume 6 is named "Dolly" but holds the same resume text

**1.5 Robustness**
- [ ] Handle OpenAI errors and timeouts (return 502/503 with a clear message instead of 500)
- [ ] Validate empty PDF text on upload
- [ ] `POST /resumes/{id}/analyze` upserts a single analysis per resume. Migration deletes older duplicate rows (keeping the highest id) and adds `UNIQUE(resume_id)`.
- [ ] `POST /api/jobs/` upserts on `job_url` (the table already has `UNIQUE(job_url)`, so a duplicate currently returns 500). The daily fetch depends on this.

**1.6 Experience parsing (approved; changes scores)**
- [ ] Parse ranges such as "Aug 2024 – Present", "Jul 2024 – Jul 2025", "2020 – 2024", "01/2023 - 06/2024", using en dash, em dash, hyphen or "to"
- [ ] Map "Present" / "Current" / "Now" to today's date
- [ ] Also accept explicit durations: "2 years", "1 yr 6 mos", "18 months"
- [ ] Calculate total experience in months; show it as "X years Y months"; compare `total_months / 12` with `required_years`
- [ ] Merge overlapping periods so concurrent jobs count once (confirmed)
- [ ] Return `total_experience_months` in the match result for transparency
- [ ] Unit tests covering every format above, using a fixed "today"

**1.7 Tests**
- [ ] pytest for the pure functions in `match_engine` (`normalize_skill`, skill and experience scoring, thresholds) as a regression guard for the "logic intact" rule
- [ ] API tests against a test DB with OpenAI and embeddings mocked

## Phase 2 — Scalability

- [ ] **Background jobs:** LLM analysis and embedding calls take seconds, so move them to a worker queue (e.g. arq/Celery with Redis). Endpoints return `202` plus a status the frontend can poll.
- [ ] **Batch embeddings:** `skill_matcher` makes N×M per-skill calls; batch-embed all uncached skills in one request
- [ ] **Vector indexes:** HNSW index on `embeddings.embedding` and `skill_embeddings.embedding`
- [ ] **One-to-many matching:** match one resume against many jobs (pgvector ANN prefilter, then deterministic scoring on the top-K)
- [ ] **Pagination** on list endpoints
- [ ] **Shared file storage:** resume PDFs on a Docker volume mounted at `FILES_DIR` in every backend/worker container
- [ ] **Stateless API** (no in-process state) so several backend containers can run side by side (`docker compose up --scale backend=N` behind a reverse proxy)
- [ ] Structured logging; `/health` endpoint

## Phase 3 — Local Docker deployment

The whole stack runs on this machine with one command: `docker compose up -d --build`.

- [ ] **Dockerfiles:** backend (Python slim + uvicorn), worker (same image, different command), frontend (`next build` + `next start`)
- [ ] **Compose services:** `postgres`, `n8n`, `redis`, `migrate` (one-shot `alembic upgrade head`), `backend`, `worker`, `frontend`; `depends_on` with healthchecks so each waits for what it needs
- [ ] **Container settings:** `POSTGRES_HOST=postgres`, `FILES_DIR=/data/files` on the `./files` bind mount, `CORS_ORIGINS=http://localhost:3000`
- [ ] **Frontend API URL:** the browser runs on the host, so `NEXT_PUBLIC_API_URL=http://localhost:8000` as a build arg. Next.js inlines it at build time, so changing it means rebuilding the image; alternatively Next proxies `/api` to `http://backend:8000` (same origin, no CORS)
- [ ] **n8n → backend:** Phase 4 workflows call `http://backend:8000` over the compose network
- [ ] **Secrets** stay in `.env` (`env_file`), never baked into images
- [ ] **Persistence:** named volumes for Postgres and n8n data; `./files` for PDFs
- [ ] **Backups:** script that runs `pg_dump` for `resume_app` and `n8n` into `backups/` with dated filenames
- [ ] **Local-only exposure:** publish ports on `127.0.0.1` only
- [ ] **Always-on caveat:** schedules only fire while Docker is running. Enable Docker Desktop autostart, and make the daily fetch catch up on start if today's run was missed (the 15-minute email dispatcher already catches up by design)
- [ ] CI: lint, test, `docker compose build`

## Phase 4 — Daily job feed

The workflows below are written for n8n, the current candidate; whether to use n8n is still open (question 3). Either way, the v1 workflows stay untouched.

Fetching and emailing are separate workflows: jobs are fetched once a day, while emails go out at each user's chosen time.

```
Workflow A: Daily fetch (Schedule Trigger, once a day)
  → Fetch openings from job sources (official APIs / RSS)
  → Normalize fields → POST /api/jobs (upsert on job_url)
  → POST /api/jobs/{id}/analyze
  → POST /api/matches for each active resume
  → Portal shows them immediately (same DB)

Workflow B: Notification dispatcher (Schedule Trigger, every 15 min)
  → GET /api/notifications/due  (users whose local time has reached their chosen time and who haven't been sent today's email)
  → Build digest per user: new APPLY / CONSIDER jobs with score, matched and missing skills, link
  → n8n Gmail node (OAuth credential) → send
  → POST /api/notifications/{user_id}/sent  (records last_sent_at so nobody gets it twice)
```

**Job sources (decide together when building this phase)**
- [ ] Choose sources, locations and keywords. Candidates: Adzuna, Remotive, Greenhouse/Lever board APIs, RSS feeds.
- [ ] Use official APIs and feeds only. Scraping sites like LinkedIn or Indeed breaks their terms of service.

**Backend**
- [ ] `source`, `posted_at`, `first_seen_at`, `is_active` columns on `jobs`; mark jobs inactive when they disappear from the feed
- [ ] `GET /api/jobs?since=&source=&recommendation=` plus a `GET /api/matches?resume_id=` listing
- [ ] One endpoint that runs ingest → analyze → match, so n8n only calls one thing per job
- [ ] **Users and notification settings:** there is no user concept yet. Add a `users` table (email, linked resume(s)) and `notification_settings` (`enabled`, `send_time`, `timezone`, `min_recommendation`, `last_sent_at`). Authentication method to be decided.
- [ ] `GET /api/notifications/due` and `POST /api/notifications/{user_id}/sent` for the dispatcher

**Portal**
- [ ] "New today" badge, filter and sort by score or recommendation, show match results on the jobs list
- [ ] **Settings page:** turn daily email on or off, pick a time with a time picker, time zone (defaults to the browser's), minimum recommendation to include

**Email**
- [ ] n8n Gmail node with an HTML digest; skip sending when nothing new reaches the user's minimum recommendation
- [ ] Unsubscribe or "change time" link back to the settings page
- [ ] Gmail sending limits (~500/day for a personal account, ~2,000 for Workspace) are fine for now; switch to a transactional email provider if the user count grows

## Phase 5 — Agents (where applicable)

Agents gather, normalize and explain. They never set the score; that stays deterministic.

- [ ] **Job ingestion agent:** given a job URL, fetch the page and extract company, title and description into `POST /api/jobs`
- [ ] **Skill normalization agent:** maintain a canonical skill taxonomy and synonyms ("Postgres" = "PostgreSQL") that feeds `skill_matcher` / `normalize_skill`
- [ ] **Match explanation agent:** read-only. From stored evidence (matched/missing skills, experience), write a recruiter summary and resume-gap suggestions.
- [ ] **Orchestration:** add a v2 n8n workflow that calls the FastAPI endpoints (upload → analyze → match → notify) alongside the untouched v1 workflows
- [ ] **Evaluation set:** fixed resume/job pairs with expected recommendations, to catch regressions when prompts or models change

### Additional features (approved 2026-10-28)

- [ ] **Career-page scraper agent in a throwaway container:** for companies without a job API, an agent writes extraction code that runs in a disposable, locked-down Docker container (no host mounts, read-only filesystem, CPU/memory/time limits). Untrusted pages and generated code never touch the main app. Use a small dedicated runner service rather than giving the backend access to the Docker socket. Output goes into the Phase 4 feed.
- [ ] **Cross-source duplicate detection:** the same job is often posted on several boards with different URLs. Use job embeddings with a high similarity threshold to merge them, so the email doesn't list the same role twice.
- [ ] **Weekly skill-gap trends:** combine `missing_skills` across the week's matched jobs, e.g. "Kubernetes appears in 40% of your CONSIDER jobs." Show it on the portal and in a weekly email.
- [ ] **Resume tailoring suggestions:** for APPLY/CONSIDER jobs, suggest how to reword existing resume bullets toward the job, using only evidence already in the resume. The score is unaffected.
- [ ] **User feedback signals:** "Applied" / "Not interested" buttons on the portal and in the email. They filter future emails and grow the evaluation set without touching the scoring formula.

---

## Open questions

1. Job sources, locations and keywords for the daily feed (decide together during Phase 4).
2. How users sign in, now that per-user settings are needed (decide when Phase 4 starts).
3. **n8n's role (decide later, per user 2026-10-30):** whether and how the v1 workflows and the Phase 4 scheduled workflows keep using n8n. Until then, don't change n8n credentials or drop the old tables in the `n8n` database.
