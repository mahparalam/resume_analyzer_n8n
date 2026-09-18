from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ResumeJobMatch(Base):
    __tablename__ = "resume_job_matches"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id"),
        nullable=False
    )

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id"),
        nullable=False
    )

    match_score: Mapped[int | None] = mapped_column(
        Integer
    )

    matched_skills: Mapped[str | None] = mapped_column(
        Text
    )

    missing_skills: Mapped[str | None] = mapped_column(
        Text
    )

    experience_match: Mapped[str | None] = mapped_column(
        String(100)
    )

    recommendation: Mapped[str | None] = mapped_column(
        String(50)
    )