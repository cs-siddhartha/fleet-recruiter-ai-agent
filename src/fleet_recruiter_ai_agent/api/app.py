from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from fleet_recruiter_ai_agent.config import settings
from fleet_recruiter_ai_agent.data.jobs import get_job, list_jobs
from fleet_recruiter_ai_agent.schemas.jobs import JobDetail, JobSummary


app = FastAPI(title=settings.app_name)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/jobs", response_model=list[JobSummary])
def get_jobs() -> list[JobSummary]:
    """Return the backend-owned jobs available for candidate evaluation."""

    return [JobSummary(**job.model_dump()) for job in list_jobs()]


@app.get("/api/jobs/{job_id}", response_model=JobDetail)
def get_job_detail(job_id: str) -> JobDetail:
    """Return the full job description for a selected backend-owned job."""

    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job
