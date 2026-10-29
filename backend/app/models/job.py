from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("job_url", name="jobs_job_url_unique"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    company: Mapped[str | None] = mapped_column(
        String(255)
    )

    job_title: Mapped[str | None] = mapped_column(
        String(255)
    )

    job_url: Mapped[str | None] = mapped_column(
        Text
    )

    match_score: Mapped[int | None] = mapped_column(
        Integer
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        server_default=text("CURRENT_TIMESTAMP")
    )

    job_description: Mapped[str | None] = mapped_column(
        Text
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
