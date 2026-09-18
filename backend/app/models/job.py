from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Job(Base):
    __tablename__ = "jobs"

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

    job_description: Mapped[str | None] = mapped_column(
        Text
    )

    matched_skills: Mapped[str | None] = mapped_column(
        Text
    )