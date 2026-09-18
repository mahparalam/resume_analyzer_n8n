from pydantic import BaseModel


class ResumeCreate(BaseModel):
    name: str
    email: str
    resume_text: str


class ResumeResponse(BaseModel):
    id: int
    name: str | None = None
    email: str | None = None
    resume_text: str | None = None

class ResumeUpdate(BaseModel):
    name: str
    email: str
    resume_text: str
