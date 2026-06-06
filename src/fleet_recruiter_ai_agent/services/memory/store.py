from redis import Redis

from fleet_recruiter_ai_agent.schemas.memory import JobMemory


class RedisMemoryStore:  # pylint: disable=too-few-public-methods
    """Persist one analyzed job-memory document under each job ID.

    Applications always target a known job, so Redis can retrieve the complete reusable
    JD context directly without ranking records. Rewriting the same key also keeps memory
    synchronized when a recruiter updates and re-analyzes a job.
    """

    def __init__(
        self,
        redis_url: str,
        namespace: str,
        client: Redis | None = None,
    ) -> None:
        """Create a decoded Redis client and retain the application key namespace."""

        self._client = client or Redis.from_url(redis_url, decode_responses=True)
        self._namespace = namespace

    def upsert(self, memory: JobMemory) -> None:
        """Create or replace the complete analyzed memory for one job."""

        self._client.set(self._key(memory.job_id), memory.model_dump_json())

    def get(self, job_id: str) -> JobMemory | None:
        """Return validated memory for a job, or None when it has not been indexed."""

        payload = self._client.get(self._key(job_id))
        if payload is None:
            return None
        return JobMemory.model_validate_json(payload)

    def ping(self) -> bool:
        """Report whether the configured Redis server is reachable."""

        return bool(self._client.ping())

    def _key(self, job_id: str) -> str:
        """Build the exact Redis key used to isolate one job's analyzed memory."""

        return f"{self._namespace}:job-memory:{job_id}"
