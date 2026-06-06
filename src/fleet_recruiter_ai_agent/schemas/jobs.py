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


class JobWrite(BaseModel):
    """Validate recruiter-owned fields used to create or replace a job.

    The backend owns job IDs so callers cannot overwrite another job by choosing an
    identifier. The same payload supports creation and full updates while API handlers
    preserve the existing ID when replacing a job.
    """

    title: str = Field(min_length=1)
    company: str = Field(min_length=1)
    location: str = Field(min_length=1)
    summary: str = Field(min_length=1)
    job_description: str = Field(min_length=1)
