-- Resume Intelligence Platform: application database schema
-- GENERATED from Alembic migrations; do not edit by hand.
-- Regenerate: cd backend && alembic upgrade head --sql > ../schema.sql
-- Apply to a database: cd backend && alembic upgrade head

BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> df775c301f09

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE embeddings (
    id SERIAL NOT NULL, 
    entity_type VARCHAR(50) NOT NULL, 
    entity_id INTEGER NOT NULL, 
    content_hash VARCHAR(64) NOT NULL, 
    embedding VECTOR(1536) NOT NULL, 
    model VARCHAR(100) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    PRIMARY KEY (id), 
    UNIQUE (entity_type, entity_id)
);

CREATE TABLE jobs (
    id SERIAL NOT NULL, 
    company VARCHAR(255), 
    job_title VARCHAR(255), 
    job_url TEXT, 
    match_score INTEGER, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    job_description TEXT, 
    matched_skills TEXT, 
    missing_skills TEXT, 
    experience_match VARCHAR(100), 
    recommendation VARCHAR(50), 
    PRIMARY KEY (id), 
    CONSTRAINT jobs_job_url_unique UNIQUE (job_url)
);

CREATE TABLE resumes (
    id SERIAL NOT NULL, 
    name VARCHAR(255), 
    email VARCHAR(255), 
    resume_text TEXT, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    file_path TEXT, 
    PRIMARY KEY (id)
);

CREATE TABLE skill_embeddings (
    id SERIAL NOT NULL, 
    skill_text TEXT NOT NULL, 
    normalized_text TEXT NOT NULL, 
    embedding VECTOR(1536) NOT NULL, 
    model VARCHAR(100) NOT NULL, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    PRIMARY KEY (id), 
    UNIQUE (normalized_text)
);

CREATE TABLE job_requirements (
    id SERIAL NOT NULL, 
    job_id INTEGER NOT NULL, 
    required_skills JSONB, 
    preferred_skills JSONB, 
    experience_years INTEGER, 
    education JSONB, 
    responsibilities JSONB, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    PRIMARY KEY (id), 
    FOREIGN KEY(job_id) REFERENCES jobs (id) ON DELETE CASCADE
);

CREATE TABLE resume_analyses (
    id SERIAL NOT NULL, 
    resume_id INTEGER NOT NULL, 
    summary TEXT, 
    skills JSONB, 
    experience JSONB, 
    education JSONB, 
    projects JSONB, 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    PRIMARY KEY (id), 
    FOREIGN KEY(resume_id) REFERENCES resumes (id) ON DELETE CASCADE
);

CREATE TABLE resume_job_matches (
    id SERIAL NOT NULL, 
    resume_id INTEGER NOT NULL, 
    job_id INTEGER NOT NULL, 
    match_score INTEGER, 
    matched_skills TEXT, 
    missing_skills TEXT, 
    experience_match VARCHAR(100), 
    recommendation VARCHAR(50), 
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP, 
    PRIMARY KEY (id), 
    FOREIGN KEY(job_id) REFERENCES jobs (id), 
    FOREIGN KEY(resume_id) REFERENCES resumes (id), 
    CONSTRAINT resume_job_matches_unique UNIQUE (resume_id, job_id)
);

INSERT INTO alembic_version (version_num) VALUES ('df775c301f09') RETURNING alembic_version.version_num;

-- Running upgrade df775c301f09 -> ed0f70a867de

UPDATE resumes
        SET file_path = substr(file_path, length('../files/') + 1)
        WHERE file_path LIKE '../files/%';

UPDATE alembic_version SET version_num='ed0f70a867de' WHERE alembic_version.version_num = 'df775c301f09';

COMMIT;
