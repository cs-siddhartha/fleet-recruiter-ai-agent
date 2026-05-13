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


class ResumeAnalysis(BaseModel):
    """Structured candidate signals extracted from a parsed resume."""

    candidate_name: str = Field(min_length=1)
    headline: str = Field(min_length=1)
    skills: list[str] = Field(default_factory=list)
    experience_summary: str = Field(min_length=1)
    impact_highlights: list[str] = Field(default_factory=list)
    projects: list[str] = Field(default_factory=list)
    public_links: list[str] = Field(default_factory=list)
    risks_or_gaps: list[str] = Field(default_factory=list)
    notes: str = Field(min_length=1)


class ScorecardCategory(BaseModel):
    """One scored section of the candidate evaluation."""

    name: str = Field(min_length=1)
    score: float = Field(ge=0, le=1)
    comment: str = Field(min_length=1)
    evidence: list[str] = Field(default_factory=list)


class CandidateScorecard(BaseModel):
    """Explainable final candidate evaluation without a hard pass/fail decision."""

    candidate_name: str = Field(min_length=1)
    job_title: str = Field(min_length=1)
    overall_score: float = Field(ge=0, le=1)
    summary: str = Field(min_length=1)
    categories: list[ScorecardCategory] = Field(min_length=1)
    missing_information: list[str] = Field(default_factory=list)
    risks_or_concerns: list[str] = Field(default_factory=list)
    interview_questions: list[str] = Field(default_factory=list)
    confidence: float = Field(ge=0, le=1)
