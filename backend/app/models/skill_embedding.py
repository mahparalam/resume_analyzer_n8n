from datetime import datetime

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Integer, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class SkillEmbedding(Base):
    __tablename__ = "skill_embeddings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    skill_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    normalized_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(1536),
        nullable=False,
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        server_default=text("CURRENT_TIMESTAMP"),
    )