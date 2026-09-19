from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ResumeAnalysis(Base):
    __tablename__ = "resume_analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=False
    )

    summary: Mapped[str | None] = mapped_column(Text)
    skills: Mapped[list | None] = mapped_column(JSONB)
    experience: Mapped[list | None] = mapped_column(JSONB)
    education: Mapped[list | None] = mapped_column(JSONB)
    projects: Mapped[list | None] = mapped_column(JSONB)

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )