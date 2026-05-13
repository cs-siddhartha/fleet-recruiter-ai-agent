import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr


load_dotenv()


class Settings(BaseModel):

    app_name: str = "Fleet Recruiter AI Agent"
    min_match_score: float = Field(default=0.7, ge=0, le=1)
    max_candidates: int = Field(default=25, ge=1, le=500)
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-5.5"
    github_api_base_url: str = "https://api.github.com"
    public_fetch_timeout_seconds: float = Field(default=8, ge=1, le=30)


def load_settings() -> Settings:
    """Load application settings from `.env` and process environment variables."""

    openai_api_key = os.getenv("OPENAI_API_KEY")
    return Settings(
        app_name=os.getenv("APP_NAME", "Fleet Recruiter AI Agent"),
        min_match_score=float(os.getenv("MIN_MATCH_SCORE", "0")),
        max_candidates=int(os.getenv("MAX_CANDIDATES", "0")),
        openai_api_key=SecretStr(openai_api_key) if openai_api_key else None,
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        github_api_base_url=os.getenv("GITHUB_API_BASE_URL", "https://api.github.com"),
        public_fetch_timeout_seconds=float(os.getenv("PUBLIC_FETCH_TIMEOUT_SECONDS", "8")),
    )


settings = load_settings()
