from pydantic import BaseModel


class JobRequirement(BaseModel):
    required_skills: list[str]
    preferred_skills: list[str]
    experience_years: int | None = None
    education: list[str]
    responsibilities: list[str]