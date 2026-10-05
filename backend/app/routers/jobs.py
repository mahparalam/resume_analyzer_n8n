from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.job import Job
from app.schemas.job import JobCreate, JobResponse, JobUpdate
from app.models.job_requirement import JobRequirement
from app.services.job_analyzer import analyze_job

router = APIRouter(prefix="/api/jobs")

@router.post("/", response_model=JobResponse, status_code=201)
def create_job(job: JobCreate, db: Session = Depends(get_db)):

    new_job = Job(
        company=job.company,
        job_title=job.job_title,
        job_url=job.job_url,
        job_description=job.job_description
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return new_job

@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: int, db: Session = Depends(get_db)):

    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    return job

@router.get("/", response_model=List[JobResponse])
def get_jobs(db: Session = Depends(get_db)):
    jobs = db.query(Job).all()

    return jobs

@router.put("/{job_id}", response_model=JobResponse)
def update_job(
    job_id: int,
    job_data: JobUpdate,
    db: Session = Depends(get_db)
):

    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    job.company = job_data.company
    job.job_title = job_data.job_title
    job.job_url = job_data.job_url
    job.job_description = job_data.job_description

    db.commit()
    db.refresh(job)

    return job

@router.delete("/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):

    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found"
        )

    db.delete(job)
    db.commit()
    return {"message": "Job deleted successfully"}

@router.post("/{job_id}/analyze")
def analyze_job_endpoint(
    job_id: int,
    db: Session = Depends(get_db),
):
    # 1. Find the job
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    # 2. Make sure the job has a description
    if not job.job_description:
        raise HTTPException(
            status_code=400,
            detail="Job description is empty",
        )

    # 3. Send the description to the AI analyzer
    analysis = analyze_job(job.job_description)

    # 4. Save the structured requirements
    requirements = (
    db.query(JobRequirement)
    .filter(JobRequirement.job_id == job.id)
    .first()
)

    if requirements is None:
        requirements = JobRequirement(
            job_id=job.id,
        )
        db.add(requirements)

    requirements.required_skills = analysis.required_skills
    requirements.preferred_skills = analysis.preferred_skills
    requirements.experience_years = analysis.experience_years
    requirements.education = analysis.education
    requirements.responsibilities = analysis.responsibilities

    db.commit()
    db.refresh(requirements)

    # 5. Return the result
    return {
        "job_id": job.id,
        "requirements": analysis,
    }

@router.get("/{job_id}/requirements")
def get_job_requirements(
    job_id: int,
    db: Session = Depends(get_db),
):
    job = db.get(Job, job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Job not found",
        )

    requirements = (
        db.query(JobRequirement)
        .filter(JobRequirement.job_id == job_id)
        .order_by(JobRequirement.id.desc())
        .first()
    )

    if requirements is None:
        raise HTTPException(
            status_code=404,
            detail="Job requirements not found",
        )

    return requirements