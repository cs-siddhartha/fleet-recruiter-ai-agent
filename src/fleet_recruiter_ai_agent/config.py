from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="FLEET_")

    app_name: str = "Fleet Recruiter AI Agent"
    min_match_score: float = Field(default=0.7, ge=0, le=1)
    max_candidates: int = Field(default=25, ge=1, le=500)


settings = Settings()
