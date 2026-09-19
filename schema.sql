-- Resume Analyzer v1
-- PostgreSQL database schema

CREATE TABLE IF NOT EXISTS resumes (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    email VARCHAR(255),
    resume_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    company VARCHAR(255),
    job_title VARCHAR(255),
    job_url TEXT,
    match_score INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    job_description TEXT,
    matched_skills TEXT,
    missing_skills TEXT,
    experience_match VARCHAR(100),
    recommendation VARCHAR(50),

    CONSTRAINT jobs_job_url_unique UNIQUE (job_url)
);

CREATE TABLE IF NOT EXISTS resume_job_matches (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL REFERENCES resumes(id),
    job_id INTEGER NOT NULL REFERENCES jobs(id),
    match_score INTEGER,
    matched_skills TEXT,
    missing_skills TEXT,
    experience_match VARCHAR(100),
    recommendation VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT resume_job_matches_unique UNIQUE (resume_id, job_id)
);

CREATE TABLE IF NOT EXISTS resume_analyses (
    id SERIAL PRIMARY KEY,
    resume_id INTEGER NOT NULL REFERENCES resumes(id) ON DELETE CASCADE,
    summary TEXT,
    skills JSONB,
    experience JSONB,
    education JSONB,
    projects JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);