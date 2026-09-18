from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    company: str
    job_title: str
    job_url: str | None = None
    job_description: str | None = None


class JobResponse(BaseModel):
    id: int
    company: str | None = None
    job_title: str | None = None
    job_url: str | None = None
    job_description: str | None = None
    match_score: int | None = None
    matched_skills: str | None = None


class JobUpdate(BaseModel):
    company: str
    job_title: str
    job_url: str | None = None
    job_description: str | None = None