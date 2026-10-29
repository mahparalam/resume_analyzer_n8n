import hashlib
import os

from dotenv import load_dotenv
from openai import OpenAI
from sqlalchemy.orm import Session

from app.models.embedding import Embedding

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

EMBEDDING_MODEL = "text-embedding-3-small"


def create_content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def create_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response.data[0].embedding


def get_or_create_embedding(
    db: Session,
    entity_type: str,
    entity_id: int,
    text: str,
) -> Embedding:

    content_hash = create_content_hash(text)

    existing = (
        db.query(Embedding)
        .filter(
            Embedding.entity_type == entity_type,
            Embedding.entity_id == entity_id,
        )
        .first()
    )

    if existing and existing.content_hash == content_hash:
        return existing

    vector = create_embedding(text)

    if existing:
        existing.content_hash = content_hash
        existing.embedding = vector
        existing.model = EMBEDDING_MODEL
    else:
        existing = Embedding(
            entity_type=entity_type,
            entity_id=entity_id,
            content_hash=content_hash,
            embedding=vector,
            model=EMBEDDING_MODEL,
        )
        db.add(existing)

    db.commit()
    db.refresh(existing)

    return existing