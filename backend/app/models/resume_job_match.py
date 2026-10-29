from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ResumeJobMatch(Base):
    __tablename__ = "resume_job_matches"
    __table_args__ = (
        UniqueConstraint(
            "resume_id",
            "job_id",
            name="resume_job_matches_unique",
        ),
    )

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

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )
