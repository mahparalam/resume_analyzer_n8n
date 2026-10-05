import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.job import Job
from app.models.resume import Resume
from app.models.job_requirement import JobRequirement
from app.models.resume_analysis import ResumeAnalysis
from app.models.resume_job_match import ResumeJobMatch
from app.schemas.match import MatchRequest
from app.services.match_engine import calculate_match


router = APIRouter(
    prefix="/api/matches",
    tags=["matches"],
)

@router.post("/")
def create_match(
    match_data: MatchRequest,
    db: Session = Depends(get_db),
):
    # Find resume
    resume = db.get(Resume, match_data.resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    # Find job
    job = db.get(Job, match_data.job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    # Find latest resume analysis
    resume_analysis = (
        db.query(ResumeAnalysis)
        .filter(
            ResumeAnalysis.resume_id
            == match_data.resume_id
        )
        .order_by(ResumeAnalysis.id.desc())
        .first()
    )

    if resume_analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not found. Analyze the resume first.",
        )

    # Find job requirements
    job_requirements = (
        db.query(JobRequirement)
        .filter(
            JobRequirement.job_id
            == match_data.job_id
        )
        .first()
    )

    if job_requirements is None:
        raise HTTPException(
            status_code=404,
            detail="Job requirements not found. Analyze the job first.",
        )

    # Run matching engine
    result = calculate_match(
        resume_skills=resume_analysis.skills or [],
        resume_experience=resume_analysis.experience or [],
        required_skills=job_requirements.required_skills or [],
        preferred_skills=job_requirements.preferred_skills or [],
        required_years=job_requirements.experience_years,
    )

    # Check whether match already exists
    existing_match = (
        db.query(ResumeJobMatch)
        .filter(
            ResumeJobMatch.resume_id
            == match_data.resume_id,
            ResumeJobMatch.job_id
            == match_data.job_id,
        )
        .first()
    )

    if existing_match:
        match = existing_match
    else:
        match = ResumeJobMatch(
            resume_id=match_data.resume_id,
            job_id=match_data.job_id,
        )
        db.add(match)

    match.match_score = result["match_score"]
    match.matched_skills = json.dumps(
        result["matched_skills"]
    )
    match.missing_skills = json.dumps(
        result["missing_skills"]
    )
    match.experience_match = result["experience_match"]
    match.recommendation = result["recommendation"]

    db.commit()
    db.refresh(match)

    return {
        "id": match.id,
        "resume_id": match.resume_id,
        "job_id": match.job_id,
        **result,
    }