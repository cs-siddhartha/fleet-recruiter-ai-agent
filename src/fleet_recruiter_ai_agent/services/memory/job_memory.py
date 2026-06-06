from fleet_recruiter_ai_agent.config import settings
from fleet_recruiter_ai_agent.schemas.jobs import JobDetail
from fleet_recruiter_ai_agent.schemas.memory import JobMemory
from fleet_recruiter_ai_agent.services.llm import LLMClient
from fleet_recruiter_ai_agent.services.memory.store import RedisMemoryStore
from fleet_recruiter_ai_agent.tools.jd_analysis import JDAnalysisInput, analyze_jd


class JobMemoryService: 
    """Resolve reusable JD analysis before candidate-specific work begins.

    Job descriptions are shared across many applications, so analyzing them for every
    candidate wastes tokens and can produce inconsistent requirements. This service owns
    exact Redis lookup and refreshes memory whenever the job is new or its description
    has changed.
    """

    def __init__(self, store: RedisMemoryStore) -> None:
        """Retain the persistence boundary used for job-memory lookup and updates."""

        self._store = store

    def get_or_analyze(self, job: JobDetail, llm_client: LLMClient) -> JobMemory:
        """Return current job memory, analyzing and persisting the JD on a miss or edit."""

        existing = self._store.get(job.id)
        if existing is not None and existing.job_description == job.job_description:
            return existing

        analysis = analyze_jd(JDAnalysisInput(job=job), llm_client)
        memory = JobMemory(
            job_id=job.id,
            job_description=job.job_description,
            analysis=analysis,
        )
        self._store.upsert(memory)
        return memory


def build_job_memory_service() -> JobMemoryService:
    """Build the job-memory service from validated Redis application settings."""

    store = RedisMemoryStore(
        redis_url=settings.redis_url,
        namespace=settings.memory_namespace,
    )
    return JobMemoryService(store)
