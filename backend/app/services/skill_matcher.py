import re

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.models.skill_embedding import SkillEmbedding
from app.services.embedding_service import create_embedding
from app.services.match_engine import normalize_skill


def get_or_create_skill_embedding(
    db: Session,
    skill: str,
) -> SkillEmbedding:

    normalized_skill = normalize_skill(skill)

    existing = (
        db.query(SkillEmbedding)
        .filter(
            SkillEmbedding.normalized_text == normalized_skill
        )
        .first()
    )

    if existing:
        return existing

    vector = create_embedding(skill)

    skill_embedding = SkillEmbedding(
        skill_text=skill,
        normalized_text=normalized_skill,
        embedding=vector,
        model="text-embedding-3-small",
    )

    db.add(skill_embedding)
    db.commit()
    db.refresh(skill_embedding)

    return skill_embedding


def calculate_skill_similarity(
    db: Session,
    resume_skill: str,
    job_skill: str,
) -> float:

    resume_embedding = get_or_create_skill_embedding(
        db,
        resume_skill,
    )

    job_embedding = get_or_create_skill_embedding(
        db,
        job_skill,
    )

    result = db.execute(
        text(
            """
            SELECT 1 - (resume.embedding <=> job.embedding)
            FROM skill_embeddings AS resume
            CROSS JOIN skill_embeddings AS job
            WHERE resume.id = :resume_id
              AND job.id = :job_id
            """
        ),
        {
            "resume_id": resume_embedding.id,
            "job_id": job_embedding.id,
        },
    )

    similarity = result.scalar()

    if similarity is None:
        raise ValueError("Skill embedding not found")

    return float(similarity)

def find_best_skill_matches(
    db: Session,
    resume_skills: list[str],
    job_skills: list[str],
    threshold: float = 0.60,
) -> dict:
    matched = []
    missing = []

    for job_skill in job_skills:
        best_similarity = 0.0
        best_resume_skill = None

        for resume_skill in resume_skills:
            similarity = calculate_skill_similarity(
                db,
                resume_skill,
                job_skill,
            )

            if similarity > best_similarity:
                best_similarity = similarity
                best_resume_skill = resume_skill

        if best_similarity >= threshold:
            matched.append({
                "job_skill": job_skill,
                "resume_skill": best_resume_skill,
                "similarity": best_similarity,
            })
        else:
            missing.append({
                "skill": job_skill,
                "best_similarity": best_similarity,
            })

    return {
        "matched": matched,
        "missing": missing,
    }