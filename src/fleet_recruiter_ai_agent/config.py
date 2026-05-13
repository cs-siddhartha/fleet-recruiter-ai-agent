from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FLEET_")

    app_name: str = "Fleet Recruiter AI Agent"
    min_match_score: float = Field(default=0.7, ge=0, le=1)
    max_candidates: int = Field(default=25, ge=1, le=500)
    openai_api_key: SecretStr | None = None
    openai_model: str = "gpt-5.5"
    github_api_base_url: str = "https://api.github.com"
    public_fetch_timeout_seconds: float = Field(default=8, ge=1, le=30)


settings = Settings()
