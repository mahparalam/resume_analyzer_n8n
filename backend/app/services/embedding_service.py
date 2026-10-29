import hashlib
import os

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session

from app.models.embedding import Embedding
from app.models.job import Job
from app.models.job_requirement import JobRequirement
from app.models.resume_analysis import ResumeAnalysis
from app.services.embedding_text import (
    build_job_embedding_text,
    build_resume_embedding_text,
)

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"


def create_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def create_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def get_or_create_embedding(
    db: Session,
    entity_type: str,
    entity_id: int,
    text: str,
) -> Embedding:

    content_hash = create_content_hash(text)

    existing = (
        db.query(Embedding)
        .filter(
            Embedding.entity_type == entity_type,
            Embedding.entity_id == entity_id,
        )
        .first()
    )

    if existing and existing.content_hash == content_hash:
        return existing

    vector = create_embedding(text)

    if existing:
        existing.content_hash = content_hash
        existing.embedding = vector
        existing.model = EMBEDDING_MODEL
    else:
        existing = Embedding(
            entity_type=entity_type,
            entity_id=entity_id,
            content_hash=content_hash,
            embedding=vector,
            model=EMBEDDING_MODEL,
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)

    return existing


def ensure_resume_embedding(
    db: Session,
    analysis: ResumeAnalysis,
) -> Embedding:
    text = build_resume_embedding_text(
        summary=analysis.summary,
        skills=analysis.skills,
        experience=analysis.experience,
        projects=analysis.projects,
    )

    if not text:
        raise ValueError("Resume analysis has no content to embed")

    return get_or_create_embedding(
        db,
        entity_type="resume",
        entity_id=analysis.resume_id,
        text=text,
    )


def ensure_job_embedding(
    db: Session,
    job: Job,
    requirements: JobRequirement,
) -> Embedding:
    text = build_job_embedding_text(
        job_title=job.job_title,
        required_skills=requirements.required_skills,
        preferred_skills=requirements.preferred_skills,
        experience_years=requirements.experience_years,
        responsibilities=requirements.responsibilities,
    )

    if not text:
        raise ValueError("Job requirements have no content to embed")

    return get_or_create_embedding(
        db,
        entity_type="job",
        entity_id=job.id,
        text=text,
    )
