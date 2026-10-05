from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class JobRequirement(Base):
    __tablename__ = "job_requirements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
    )

    required_skills: Mapped[list | None] = mapped_column(JSONB)
    preferred_skills: Mapped[list | None] = mapped_column(JSONB)
    experience_years: Mapped[int | None] = mapped_column(Integer)
    education: Mapped[list | None] = mapped_column(JSONB)
    responsibilities: Mapped[list | None] = mapped_column(JSONB)

    created_at: Mapped[datetime | None] = mapped_column(DateTime)