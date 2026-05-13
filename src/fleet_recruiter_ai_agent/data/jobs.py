from fleet_recruiter_ai_agent.schemas.jobs import JobDetail


JOBS: tuple[JobDetail, ...] = (
    JobDetail(
        id="ai-recruiting-engineer",
        title="AI Recruiting Engineer",
        company="FleetWorks",
        location="Remote",
        summary="Build AI systems that evaluate technical talent with structured evidence.",
        job_description=(
            "Build Python services that parse resumes, analyze job descriptions, evaluate candidate fit, "
            "and produce explainable scorecards. Requires strong Python, FastAPI, Pydantic, LLM integration, "
            "API design, and practical evaluation workflows. GitHub data, public profile analysis, and "
            "human-in-the-loop recruiting experience are strong pluses."
        ),
    ),
    JobDetail(
        id="frontend-platform-engineer",
        title="Frontend Platform Engineer",
        company="FleetWorks",
        location="New York, NY",
        summary="Own fast React workflows for recruiter and candidate products.",
        job_description=(
            "Build recruiter-facing product surfaces in React and TanStack. Requires TypeScript, routing, "
            "data fetching, component design, performance, accessibility, file uploads, polling workflows, "
            "and polished operational interfaces."
        ),
    ),
    JobDetail(
        id="ml-platform-engineer",
        title="ML Platform Engineer",
        company="FleetWorks",
        location="San Francisco, CA",
        summary="Build reliable infrastructure for model-backed products and evaluation pipelines.",
        job_description=(
            "Build services for model orchestration, evaluation, observability, and production deployment. "
            "Requires Python, API design, model evaluation, data pipelines, reliable background processing, "
            "monitoring, and cloud deployment."
        ),
    ),
)


def list_jobs() -> list[JobDetail]:
    """Return all seeded jobs owned by the backend."""

    return list(JOBS)


def get_job(job_id: str) -> JobDetail | None:
    """Return one seeded job by id, or None when it does not exist."""

    return next((job for job in JOBS if job.id == job_id), None)
