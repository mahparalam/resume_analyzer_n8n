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