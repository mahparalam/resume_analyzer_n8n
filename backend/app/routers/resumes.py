import re
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from app.config import settings
from app.database import get_db
from app.models.resume import Resume
from app.models.resume_analysis import ResumeAnalysis
from app.schemas.resume import ResumeCreate, ResumeResponse, ResumeUpdate
from app.services.resume_analyzer import analyze_resume
from app.services.embedding_service import ensure_resume_embedding
from app.schemas.resume_analysis import ResumeAnalysisResponse
from pathlib import Path
from io import BytesIO
from pypdf import PdfReader
from fastapi.responses import FileResponse

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

@router.post("/upload", response_model=ResumeResponse, status_code=201)
async def upload_resume(
    file: UploadFile = File(...),
    name: str = Form(...),
    email: str = Form(...),
    db: Session = Depends(get_db),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed",
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty",
        )

    # Extract text from PDF
    try:
        pdf = PdfReader(BytesIO(contents))

        text = ""

        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="The file could not be read as a PDF",
        )

    if not text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "No text could be extracted from this PDF. "
                "It may be a scanned image; please upload a text-based PDF."
            ),
        )

    # Create database record first
    new_resume = Resume(
        name=name,
        email=email,
        resume_text=text
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    # Save original PDF using the database ID
    relative_path = Path("resumes") / f"{new_resume.id}.pdf"
    file_path = settings.files_path / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)

    file_path.write_bytes(contents)

    # Save the path relative to FILES_DIR in the database
    new_resume.file_path = relative_path.as_posix()

    db.commit()
    db.refresh(new_resume)

    return new_resume

@router.post("/{resume_id}/analyze")
def analyze_resume_endpoint(
    resume_id: int,
    db: Session = Depends(get_db)
):
    resume = db.get(Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    if not (resume.resume_text or "").strip():
        raise HTTPException(
            status_code=400,
            detail="Resume has no text to analyze",
        )

    # Send resume text to the LLM
    analysis = analyze_resume(resume.resume_text)

    # Save the AI analysis, replacing any previous one (one per resume)
    saved_analysis = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume.id)
        .first()
    )

    if saved_analysis is None:
        saved_analysis = ResumeAnalysis(resume_id=resume.id)
        db.add(saved_analysis)

    saved_analysis.summary = analysis.summary
    saved_analysis.skills = analysis.skills
    saved_analysis.experience = [
        item.model_dump()
        for item in analysis.experience
    ]
    saved_analysis.education = [
        item.model_dump()
        for item in analysis.education
    ]
    saved_analysis.projects = [
        item.model_dump()
        for item in analysis.projects
    ]
    saved_analysis.created_at = func.now()

    db.commit()
    db.refresh(saved_analysis)

    # Embed the analysis for semantic matching
    ensure_resume_embedding(db, saved_analysis)

    return {
        "resume_id": resume.id,
        "analysis": analysis
    }

@router.get("/{resume_id}/analysis", response_model=ResumeAnalysisResponse)
def get_resume_analysis(
    resume_id: int,
    db: Session = Depends(get_db)
):
    resume = db.get(Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found"
        )

    analysis = (
        db.query(ResumeAnalysis)
        .filter(ResumeAnalysis.resume_id == resume_id)
        .order_by(ResumeAnalysis.id.desc())
        .first()
    )

    if analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not found"
        )

    return analysis

@router.get("/{resume_id}/file")
def get_resume_file(
    resume_id: int,
    db: Session = Depends(get_db),
):
    resume = db.get(Resume, resume_id)

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    if not resume.file_path:
        raise HTTPException(
            status_code=404,
            detail="Original resume file not found",
        )

    file_path = settings.files_path / resume.file_path

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Original resume file not found",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"resume-{resume_id}.pdf",
    )