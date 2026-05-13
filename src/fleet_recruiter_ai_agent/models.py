from pydantic import BaseModel, EmailStr, Field, HttpUrl

from .config import settings


class CandidateProfile(BaseModel):
    """Candidate profile sample model used by the package CLI smoke path."""

    full_name: str = Field(min_length=1)
    email: EmailStr
    years_experience: float = Field(ge=0)
    skills: list[str] = Field(min_length=1)
    resume_url: HttpUrl | None = None


class JobFitResult(BaseModel):
    """Candidate-to-job fit sample model used by the package CLI smoke path."""

    candidate: CandidateProfile
    role: str = Field(min_length=1)
    match_score: float = Field(ge=0, le=1)
    rationale: str = Field(min_length=1)

    @property
    def is_recommended(self) -> bool:
        """Return whether the sample score meets the configured match threshold."""

        return self.match_score >= settings.min_match_score
