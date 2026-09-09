# AI Resume Analyzer v1

An AI-powered resume-to-job matching system built with **n8n, PostgreSQL, Docker, and OpenAI**.

The system ingests a PDF resume, extracts and stores the candidate's information, receives job descriptions through a webhook, analyzes the candidate's fit against the job requirements, calculates a deterministic match score, and stores the final recommendation.

## Overview

The Resume Analyzer combines **LLM-based evidence extraction** with **deterministic scoring**.

Instead of asking the LLM to directly decide whether a candidate is a good match, the LLM extracts structured evidence from the resume and job description. The final score is then calculated using predefined rules — this makes the scoring process more consistent, explainable, and reproducible.

## Architecture

```text
                    RESUME INGESTION

Resume PDF
    │
    ▼
Read File
    │
    ▼
Extract PDF Text
    │
    ▼
LLM Candidate Information Extraction
    │
    ▼
PostgreSQL (resumes table)


                    JOB MATCHING

Job Webhook
    │
    ▼
Job Upsert
    │
    ▼
Retrieve Resume
    │
    ▼
Prepare Match Input
    │
    ▼
LLM Requirement & Evidence Extraction
    │
    ▼
Deterministic Match Scoring
    │
    ▼
Apply / Consider / Skip
    │
    ▼
Match Upsert → PostgreSQL
```

## Tech Stack

| Layer | Tool |
|---|---|
| Workflow automation & orchestration | n8n |
| Persistent data storage | PostgreSQL |
| Local infrastructure | Docker / Docker Compose |
| LLM extraction & matching analysis | OpenAI API |
| Custom logic | JavaScript (n8n Code nodes) |
| Data operations | SQL |
| Job ingestion | REST Webhook |

## Features

**Resume Processing**
- PDF resume ingestion and text extraction
- AI-based candidate name and email extraction
- Resume text persistence in PostgreSQL

**Job Processing**
- Job ingestion through an n8n webhook
- Dynamic resume selection using `resume_id`
- Job deduplication using `job_url` — existing jobs are updated instead of duplicated

**AI Matching**

The LLM extracts:
- Required skills
- Preferred skills
- Matched required skills
- Matched preferred skills
- Missing skills
- Experience match

**Deterministic Scoring**
- The final match score is calculated outside the LLM using fixed scoring rules

**Match Persistence**
- Resume/job matching results are stored in PostgreSQL
- Duplicate resume/job matches are prevented
- Re-running an analysis updates the existing match

## Matching Logic

### Score Calculation

The total score is based on three weighted components:

| Component | Weight |
|---|---|
| Required Skills | 60% |
| Preferred Skills | 20% |
| Experience | 20% |
| **Total** | **100%** |

### Experience Scoring

| Experience Match | Score |
|---|---|
| Strong | 20 |
| Moderate | 12 |
| Weak | 5 |

### Recommendation Thresholds

| Score | Recommendation |
|---|---|
| 80–100 | Apply |
| 60–79 | Consider |
| 0–59 | Skip |

## How It Works

### 1. Resume Ingestion

The Resume Analyzer workflow reads a PDF resume and extracts its text. The extracted text is passed to an LLM to identify the candidate's name and email. The resume information and complete resume text are then stored in PostgreSQL.

### 2. Job Ingestion

The Job Workflow receives job information through an n8n webhook.

Example request:

```json
{
  "resume_id": 1,
  "company": "Example Company",
  "job_title": "AI Engineer",
  "job_url": "https://example.com/job/123",
  "job_description": "Looking for an AI Engineer with Python, LLM, RAG and Docker experience."
}
```

### 3. Job Upsert

Jobs are stored using an upsert based on `job_url`:

```sql
ON CONFLICT (job_url)
DO UPDATE
```

Submitting the same job again does not create another job record — the existing job ID is reused.

### 4. Resume Retrieval

The workflow uses the `resume_id` supplied by the webhook to retrieve the appropriate resume:

```sql
SELECT id, name, email, resume_text
FROM resumes
WHERE id = ...;
```

This allows the same workflow to analyze different resumes dynamically.

### 5. LLM Requirement Analysis

The LLM compares the resume against the job description and extracts structured evidence. It does not directly determine the final match score — it identifies which requirements are supported by evidence in the resume.

### 6. Deterministic Match Scoring

The workflow calculates the final score using predefined rules:

```
Required Skills   → 60%
Preferred Skills  → 20%
Experience        → 20%
```

This separates AI reasoning / evidence extraction from business logic / scoring, making the final recommendation more predictable and easier to modify.

### 7. Match Upsert

The final result is stored in `resume_job_matches`. The database enforces uniqueness on `(resume_id, job_id)`, so analyzing the same resume against the same job again updates the existing match instead of creating a duplicate.

## Database

The project uses three PostgreSQL tables.

### `resumes`

Stores candidate information and extracted resume text.

| Field | Description |
|---|---|
| `id` | Primary key |
| `name` | Candidate name |
| `email` | Candidate email |
| `resume_text` | Full extracted resume text |
| `created_at` | Timestamp |

### `jobs`

Stores job information. Enforces `UNIQUE(job_url)` to prevent duplicate jobs.

| Field | Description |
|---|---|
| `id` | Primary key |
| `company` | Company name |
| `job_title` | Job title |
| `job_url` | Job posting URL |
| `job_description` | Full job description |
| `created_at` | Timestamp |

### `resume_job_matches`

Stores the result of matching a resume against a job. Enforces `UNIQUE(resume_id, job_id)` to prevent duplicate matches. Foreign keys connect match records to the corresponding resume and job.

| Field | Description |
|---|---|
| `id` | Primary key |
| `resume_id` | FK → `resumes.id` |
| `job_id` | FK → `jobs.id` |
| `match_score` | Final calculated score |
| `matched_skills` | Skills matched |
| `missing_skills` | Skills missing |
| `experience_match` | Strong / Moderate / Weak |
| `recommendation` | Apply / Consider / Skip |
| `created_at` | Timestamp |

The complete schema, including constraints, is available in [`schema.sql`](./schema.sql).

## n8n Workflows

### Resume Analyzer

Responsible for resume ingestion and storage.

```
Manual Trigger → Read File → Extract PDF → Prepare Resume → OpenAI → Parse Resume Data → PostgreSQL
```

### Job Workflow

Responsible for job matching.

```
Webhook → Insert/Upsert Job → Get Resume → Prepare Match Input → OpenAI Matcher
        → Parse Match Result → Deterministic Scoring → Insert/Upsert Match
```

## Testing

The matching pipeline was tested against different job profiles:

| Job Profile | Match Score | Recommendation |
|---|---|---|
| AI Engineer | 100 | Apply |
| AI Engineer with Kubernetes/AWS requirements | 62 | Consider |
| Senior Unity Game Developer | 5 | Skip |

These tests demonstrate that the scoring system can distinguish between strong, partial, and weak matches.

### Duplicate Prevention Testing

The same job was submitted multiple times, and the same resume/job combination was analyzed multiple times. In both cases the system correctly reused the existing record instead of creating duplicates.

Verified database state:

```
Same job URL              → 1 job record
Same resume + same job    → 1 match record
```

## Running Locally

### Prerequisites

- Docker
- Docker Compose
- n8n
- PostgreSQL (provided through Docker Compose)
- An OpenAI API credential configured in n8n

### 1. Clone the Repository

```bash
git clone https://github.com/mahparalam/resume_analyzer_n8n.git
cd resume_analyzer_n8n
```

### 2. Configure Environment Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` and provide your own PostgreSQL password. **Never commit `.env` to Git.**

### 3. Start Docker Services

```bash
docker compose up -d
```

Check running containers:

```bash
docker ps
```

### 4. Open n8n

Navigate to [http://localhost:5678](http://localhost:5678).

### 5. Configure Credentials

Create/configure the required credentials in n8n:

- PostgreSQL
- OpenAI

The exported workflows contain credential references, but credentials themselves are not included in the repository.

### 6. Import the Workflows

Import into n8n:

- `Resume_Analyzer.json`
- `Job_workflow.json`

### 7. Create Database Tables

If the database tables do not already exist, run:

```bash
docker exec -i n8n-postgres psql -U n8n -d n8n < schema.sql
```

### Example Webhook Request

Once the Job Workflow is running in n8n test mode:

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

## Project Structure

```
resume_analyzer_n8n/
│
├── .env.example
├── .gitignore
├── compose.yaml
├── schema.sql
├── README.md
│
├── Job_workflow.json
└── Resume_Analyzer.json
```

Sensitive files such as `.env`, resume PDFs, and other local files are excluded through `.gitignore`.

## Project Status

### Version 1 — Complete

The current version provides an end-to-end AI resume and job matching pipeline with:

- Resume ingestion and PDF text extraction
- LLM-based information extraction
- PostgreSQL persistence
- Webhook-based job ingestion and deduplication
- LLM-based requirement/evidence extraction
- Deterministic match scoring
- Apply / Consider / Skip recommendations
- Match persistence and deduplication

### Future Improvements

- Automated job collection
- Job board/API integrations
- Improved skill normalization
- Semantic similarity using embeddings
- Vector database integration
- RAG-based resume analysis
- AI agent integration
- Web dashboard
- Application tracking
- Automated notifications
- Better evaluation and benchmarking of matching accuracy
