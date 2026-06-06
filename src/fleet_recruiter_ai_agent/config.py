import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr


load_dotenv()


class Settings(BaseModel):
    """Validated application settings loaded from environment variables."""

    app_name: str = "Fleet Recruiter AI Agent"
    min_match_score: float = Field(default=0.7, ge=0, le=1)
    max_candidates: int = Field(default=25, ge=1, le=500)
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-5.5"
    openai_embedding_model: str = "text-embedding-3-small"
    github_api_base_url: str = "https://api.github.com"
    public_fetch_timeout_seconds: float = Field(default=8, ge=1, le=30)
    redis_url: str = "redis://localhost:6379/0"
    memory_namespace: str = "fleet-recruiter"
    memory_top_k: int = Field(default=5, ge=1, le=20)
    memory_semantic_weight: float = Field(default=0.6, ge=0, le=1)
    memory_lexical_weight: float = Field(default=0.4, ge=0, le=1)
    semantic_chunk_similarity_threshold: float = Field(default=0.72, ge=0, le=1)
    semantic_chunk_max_chars: int = Field(default=1800, ge=200, le=8000)


def load_settings() -> Settings:
    """Load application settings from `.env` and process environment variables."""

    openai_api_key = os.getenv("OPENAI_API_KEY")
    return Settings(
        app_name=os.getenv("APP_NAME", "Fleet Recruiter AI Agent"),
        min_match_score=float(os.getenv("MIN_MATCH_SCORE", "0.7")),
        max_candidates=int(os.getenv("MAX_CANDIDATES", "25")),
        openai_api_key=SecretStr(openai_api_key) if openai_api_key else None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        openai_embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        github_api_base_url=os.getenv("GITHUB_API_BASE_URL", "https://api.github.com"),
        public_fetch_timeout_seconds=float(os.getenv("PUBLIC_FETCH_TIMEOUT_SECONDS", "8")),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        memory_namespace=os.getenv("MEMORY_NAMESPACE", "fleet-recruiter"),
        memory_top_k=int(os.getenv("MEMORY_TOP_K", "5")),
        memory_semantic_weight=float(os.getenv("MEMORY_SEMANTIC_WEIGHT", "0.6")),
        memory_lexical_weight=float(os.getenv("MEMORY_LEXICAL_WEIGHT", "0.4")),
        semantic_chunk_similarity_threshold=float(
            os.getenv("SEMANTIC_CHUNK_SIMILARITY_THRESHOLD", "0.72")
        ),
        semantic_chunk_max_chars=int(os.getenv("SEMANTIC_CHUNK_MAX_CHARS", "1800")),
    )


settings = load_settings()
