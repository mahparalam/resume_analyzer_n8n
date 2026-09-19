from pydantic import BaseModel


class ExperienceItem(BaseModel):
    job_title: str
    company: str
    duration: str | None = None
    responsibilities: list[str] = []


class EducationItem(BaseModel):
    degree: str
    institution: str
    duration: str | None = None


class ProjectItem(BaseModel):
    name: str
    technologies: list[str] = []
    description: str


class ResumeAnalysis(BaseModel):
    summary: str
    skills: list[str]
    experience: list[ExperienceItem]
    education: list[EducationItem]
    projects: list[ProjectItem]

class ResumeAnalysisResponse(BaseModel):
    id: int
    resume_id: int
    summary: str | None = None
    skills: list[str] | None = None
    experience: list[ExperienceItem] | None = None
    education: list[EducationItem] | None = None
    projects: list[ProjectItem] | None = None