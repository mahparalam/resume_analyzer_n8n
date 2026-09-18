from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from app.database import get_db
from app.models.resume import Resume
from app.schemas.resume import ResumeCreate, ResumeResponse, ResumeUpdate


router = APIRouter(prefix="/api/resumes")


@router.post("/", response_model=ResumeResponse, status_code=201)
def create_resume(
    resume: ResumeCreate,
    db: Session = Depends(get_db)
):
    new_resume = Resume(
        name=resume.name,
        email=resume.email,
        resume_text=resume.resume_text
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return new_resume

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    resume = db.get(Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    return resume

@router.get("/", response_model=list[ResumeResponse])
def get_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).all()

    return resumes

@router.put("/{resume_id}", response_model=ResumeResponse)
def update_resume(
    resume_id: int,
    resume_data: ResumeUpdate,
    db: Session = Depends(get_db)
):
    resume = db.get(Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    resume.name = resume_data.name
    resume.email = resume_data.email
    resume.resume_text = resume_data.resume_text

    db.commit()
    db.refresh(resume)

    return resume

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: int,
    db: Session = Depends(get_db)
):
    resume = db.get(Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    db.delete(resume)
    db.commit()

    return {"message": "Resume deleted successfully"}