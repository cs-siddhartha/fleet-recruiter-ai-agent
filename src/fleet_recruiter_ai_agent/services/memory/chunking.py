from langchain_experimental.text_splitter import SemanticChunker as LangChainSemanticChunker
from langchain_openai import OpenAIEmbeddings

from fleet_recruiter_ai_agent.config import settings


# TODO(platform): Enable this chunker when the product supports resume-to-all-jobs
# discovery. The current evaluation flow receives a job ID and retrieves its complete
# JDAnalysis directly from Redis, so semantic chunks are not created or stored yet.
class SemanticChunker:  # pylint: disable=too-few-public-methods
    """Use OpenAI embedding similarity to split source text at topic changes.

    Job memory keeps coherent source sections beside the structured JD analysis. This
    wrapper owns LangChain configuration and exposes only plain strings so the Redis
    record does not depend on LangChain document types.
    """

    def __init__(self) -> None:
        """Build a reusable LangChain semantic chunker from validated settings."""

        if settings.openai_api_key is None:
            raise RuntimeError("OPENAI_API_KEY is required for semantic chunking.")

        embeddings = OpenAIEmbeddings(
            model=settings.openai_embedding_model,
            api_key=settings.openai_api_key,
        )
        self._chunker = LangChainSemanticChunker(
            embeddings=embeddings,
            buffer_size=settings.semantic_chunk_buffer_size,
            breakpoint_threshold_type="percentile",
            breakpoint_threshold_amount=settings.semantic_chunk_breakpoint_percentile,
        )

    def split(self, text: str) -> list[str]:
        """Return semantically grouped text chunks without LangChain wrapper objects."""

        if not text.strip():
            return []
        return self._chunker.split_text(text)
