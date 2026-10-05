from pydantic import BaseModel


class MatchRequest(BaseModel):
    resume_id: int
    job_id: int


class MatchResponse(BaseModel):
    id: int
    resume_id: int
    job_id: int
    match_score: int | None
    matched_skills: list[str]
    missing_skills: list[str]
    experience_match: str | None
    recommendation: str | None