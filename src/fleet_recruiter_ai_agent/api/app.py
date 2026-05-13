from uuid import uuid4

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from fleet_recruiter_ai_agent.config import settings
from fleet_recruiter_ai_agent.data.jobs import get_job, list_jobs
from fleet_recruiter_ai_agent.schemas.evaluations import EvaluationRecord, EvaluationStage, EvaluationStatus
from fleet_recruiter_ai_agent.schemas.jobs import JobDetail, JobSummary
from fleet_recruiter_ai_agent.services.evaluation_store import evaluation_store
from fleet_recruiter_ai_agent.tools.pdf_extraction import PDFExtractionInput, extract_resume_text


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


@app.post("/api/jobs/{job_id}/evaluations", response_model=EvaluationRecord)
async def create_evaluation(job_id: str, resume: UploadFile = File(...)) -> EvaluationRecord:
    """Accept a candidate PDF resume and create an evaluation record for a job."""

    if get_job(job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    file_name = resume.filename
    if file_name is None or not file_name.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Resume must be a PDF file.")

    evaluation = EvaluationRecord(
        evaluation_id=str(uuid4()),
        job_id=job_id,
        file_name=file_name,
        status=EvaluationStatus.PENDING,
        stage=EvaluationStage.QUEUED,
    )
    evaluation_store.create(evaluation)
    evaluation_store.update_stage(evaluation.evaluation_id, EvaluationStage.PARSING_RESUME)

    content = await resume.read()
    try:
        parsed_resume = extract_resume_text(PDFExtractionInput(file_name=file_name, content=content))
    except ValueError as exc:
        return evaluation_store.fail(evaluation.evaluation_id, str(exc))

    return evaluation_store.save_resume_text(evaluation.evaluation_id, parsed_resume.text)


@app.get("/api/evaluations/{evaluation_id}", response_model=EvaluationRecord)
def get_evaluation(evaluation_id: str) -> EvaluationRecord:
    """Return the current status for a candidate resume evaluation."""

    evaluation = evaluation_store.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
    return evaluation
