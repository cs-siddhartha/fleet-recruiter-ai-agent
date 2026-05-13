from pydantic import BaseModel, EmailStr, Field, HttpUrl


class CandidateProfile(BaseModel):
    full_name: str = Field(min_length=1)
    email: EmailStr
    years_experience: float = Field(ge=0)
    skills: list[str] = Field(min_length=1)
    resume_url: HttpUrl | None = None


class JobFitResult(BaseModel):
    candidate: CandidateProfile
    role: str = Field(min_length=1)
    match_score: float = Field(ge=0, le=1)
    rationale: str = Field(min_length=1)

    @property
    def is_recommended(self) -> bool:
        from .config import settings

        return self.match_score >= settings.min_match_score
