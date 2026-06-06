from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, HTTPException, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

from fleet_recruiter_ai_agent.config import settings
from fleet_recruiter_ai_agent.data.jobs import create_job, get_job, list_jobs, update_job
from fleet_recruiter_ai_agent.schemas.evaluations import EvaluationRecord, EvaluationStage, EvaluationStatus
from fleet_recruiter_ai_agent.schemas.jobs import JobDetail, JobSummary, JobWrite
from fleet_recruiter_ai_agent.services.evaluation_store import evaluation_store
from fleet_recruiter_ai_agent.services.evaluator import run_evaluation
from fleet_recruiter_ai_agent.services.llm import LLMClient
from fleet_recruiter_ai_agent.services.memory import build_job_memory_service


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


@app.post("/api/jobs", response_model=JobDetail, status_code=status.HTTP_201_CREATED)
def post_job(payload: JobWrite) -> JobDetail:
    """Create a job only after its reusable JD analysis is stored in Redis."""

    job = JobDetail(id=str(uuid4()), **payload.model_dump())
    _index_job_memory(job)
    return create_job(job)


@app.put("/api/jobs/{job_id}", response_model=JobDetail)
def put_job(job_id: str, payload: JobWrite) -> JobDetail:
    """Replace a job and refresh Redis memory before publishing the new description."""

    if get_job(job_id) is None:
        raise HTTPException(status_code=404, detail="Job not found.")

    job = JobDetail(id=job_id, **payload.model_dump())
    _index_job_memory(job)
    return update_job(job)


@app.post("/api/jobs/{job_id}/evaluations", response_model=EvaluationRecord)
async def create_evaluation(
    job_id: str,
    background_tasks: BackgroundTasks,
    resume: UploadFile = File(...),
) -> EvaluationRecord:
    """Accept a candidate PDF resume and create an evaluation record for a job."""

    job = get_job(job_id)
    if job is None:
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
    content = await resume.read()
    background_tasks.add_task(run_evaluation, evaluation.evaluation_id, job, file_name, content)
    return evaluation


@app.get("/api/evaluations/{evaluation_id}", response_model=EvaluationRecord)
def get_evaluation(evaluation_id: str) -> EvaluationRecord:
    """Return the current status for a candidate resume evaluation."""

    evaluation = evaluation_store.get(evaluation_id)
    if evaluation is None:
        raise HTTPException(status_code=404, detail="Evaluation not found.")
    return evaluation


def _index_job_memory(job: JobDetail) -> None:
    """Analyze and persist a job before API callers can submit candidates against it."""

    llm_client = LLMClient()
    memory_service = build_job_memory_service()
    memory_service.get_or_analyze(job, llm_client)
