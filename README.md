# AI Resume Analyzer v1

An AI-powered resume-to-job matching workflow built with n8n, PostgreSQL, Docker, and OpenAI.

The system accepts a resume, stores the extracted resume data, receives job descriptions through a webhook, analyzes the candidate's fit against the job requirements, calculates a deterministic match score, and stores the result.

## Architecture

Resume PDF
    ↓
Extract Resume Text
    ↓
LLM Candidate Information Extraction
    ↓
PostgreSQL (Resumes)
    ↓

Job Webhook
    ↓
PostgreSQL Job Upsert
    ↓
Retrieve Resume
    ↓
LLM Requirement & Evidence Extraction
    ↓
Deterministic Match Scoring
    ↓
PostgreSQL Match Upsert
    ↓
Apply / Consider / Skip

## Tech Stack

- n8n
- PostgreSQL
- Docker / Docker Compose
- OpenAI API
- Python/JavaScript-style workflow logic
- REST Webhooks
- SQL

## Features

- PDF resume text extraction
- AI-based candidate information extraction
- PostgreSQL resume storage
- Dynamic resume selection using `resume_id`
- Job ingestion through webhook
- Job deduplication using `job_url`
- LLM-based requirement and evidence extraction
- Deterministic match scoring
- Apply / Consider / Skip recommendations
- Resume-job match storage
- Duplicate match prevention

## Match Scoring

The scoring system uses:

- Required skills: 60%
- Preferred skills: 20%
- Experience: 20%

Recommendations:

| Score | Recommendation |
|---|---|
| 80–100 | Apply |
| 60–79 | Consider |
| 0–59 | Skip |

Experience scoring:

| Experience | Score |
|---|---:|
| Strong | 20 |
| Moderate | 12 |
| Weak | 5 |

## Database

The application uses three PostgreSQL tables:

### `resumes`

Stores candidate resume information and extracted resume text.

### `jobs`

Stores job information.

A unique constraint on `job_url` prevents duplicate job records.

### `resume_job_matches`

Stores the result of matching a resume against a job.

A unique constraint on `(resume_id, job_id)` prevents duplicate match records.

## n8n Workflows

### Resume Analyzer

Handles resume ingestion:

`PDF → Text Extraction → AI Extraction → PostgreSQL`

### Job Workflow

Handles job matching:

`Webhook → Job Upsert → Resume Retrieval → AI Matching → Deterministic Scoring → Match Upsert`

## Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd n8n-docker
