from functools import cached_property
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL

# backend/app/config.py -> repo root
REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings, read from environment variables and the
    repo-root .env file. Environment variables take precedence."""

    model_config = SettingsConfigDict(
        env_file=REPO_ROOT / ".env",
        extra="ignore",
    )

    # Database: DATABASE_URL wins; otherwise built from the parts below
    database_url: str | None = None
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = ""
    postgres_password: str = ""
    app_db: str = "resume_app"

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-5.6-luna"
    embedding_model: str = "text-embedding-3-small"

    # Uploaded resume PDFs; relative paths are resolved from the repo root
    files_dir: Path = Path("files")

    # Comma-separated list of origins allowed to call the API
    cors_origins: str = "http://localhost:3000"

    @cached_property
    def sqlalchemy_url(self) -> str:
        if self.database_url:
            return self.database_url

        return URL.create(
            drivername="postgresql",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_port,
            database=self.app_db,
        ).render_as_string(hide_password=False)

    @cached_property
    def files_path(self) -> Path:
        if self.files_dir.is_absolute():
            return self.files_dir

        return REPO_ROOT / self.files_dir

    @cached_property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
