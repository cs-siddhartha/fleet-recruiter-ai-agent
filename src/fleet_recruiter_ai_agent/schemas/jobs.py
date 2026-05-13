from pydantic import BaseModel, Field


class JobSummary(BaseModel):
    """Public summary for a job shown in the job list."""

    id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = Field(min_length=1)
    summary: str = Field(min_length=1)


class JobDetail(JobSummary):
    """Full job detail including the backend-owned job description."""

    job_description: str = Field(min_length=1)
