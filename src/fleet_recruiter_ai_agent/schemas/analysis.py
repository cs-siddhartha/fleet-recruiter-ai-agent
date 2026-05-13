from pydantic import BaseModel, Field


class JDAnalysis(BaseModel):
    """Structured requirements extracted from a backend-owned job description."""

    role_title: str = Field(min_length=1)
    must_have_skills: list[str] = Field(default_factory=list)
    nice_to_have_skills: list[str] = Field(default_factory=list)
    responsibilities: list[str] = Field(default_factory=list)
    impact_expectations: list[str] = Field(default_factory=list)
    domain_signals: list[str] = Field(default_factory=list)
    notes: str = Field(min_length=1)
