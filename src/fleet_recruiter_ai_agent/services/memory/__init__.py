"""Memory services for exact job-context persistence and retrieval."""

from fleet_recruiter_ai_agent.services.memory.store import RedisMemoryStore


# TODO(platform): Export SemanticChunker when resume-to-all-jobs discovery requires
# semantic indexing. Exact job-ID retrieval does not need chunking or vector search.
__all__ = ["RedisMemoryStore"]
