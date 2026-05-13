from fleet_recruiter_ai_agent.schemas.jobs import JobDetail


JOBS: tuple[JobDetail, ...] = (
    JobDetail(
        id="ai-recruiting-engineer",
        title="AI Recruiting Engineer",
        company="FleetWorks",
        location="Remote",
        summary="Build AI systems that evaluate technical talent with structured evidence.",
        job_description="""Build Python services that parse resumes, analyze job descriptions,
evaluate candidate fit, and produce explainable scorecards.

Key requirements:
- Strong Python, FastAPI, and Pydantic experience
- LLM integration and structured-output workflows
- API design and practical evaluation systems
- GitHub data or public profile analysis experience
- Clear documentation and modular tool design

Nice to have:
- Human-in-the-loop recruiting product experience
- Experience building evidence-backed AI workflows""",
    ),
    JobDetail(
        id="frontend-platform-engineer",
        title="Frontend Platform Engineer",
        company="FleetWorks",
        location="New York, NY",
        summary="Own fast React workflows for recruiter and candidate products.",
        job_description="""Build recruiter-facing product surfaces in React and TanStack.

Key requirements:
- Strong TypeScript and React experience
- Routing, data fetching, and component design
- Performance optimization and accessibility
- File upload and polling workflows
- Polished operational interfaces for repeated use

Nice to have:
- Experience with API-backed dashboards
- Ability to turn ambiguous workflows into simple product surfaces""",
    ),
    JobDetail(
        id="ml-platform-engineer",
        title="ML Platform Engineer",
        company="FleetWorks",
        location="San Francisco, CA",
        summary="Build reliable infrastructure for model-backed products and evaluation pipelines.",
        job_description="""Build services for model orchestration, evaluation, observability, and production deployment.

Key requirements:
- Python and API design
- Model evaluation and data pipeline experience
- Reliable background processing
- Monitoring and cloud deployment
- Quality gates for model-backed systems

Nice to have:
- LLM structured-output experience
- Experiment tracking or evaluation infrastructure experience""",
    ),
)


def list_jobs() -> list[JobDetail]:
    """Return all seeded jobs owned by the backend."""

    return list(JOBS)


def get_job(job_id: str) -> JobDetail | None:
    """Return one seeded job by id, or None when it does not exist."""

    return next((job for job in JOBS if job.id == job_id), None)
