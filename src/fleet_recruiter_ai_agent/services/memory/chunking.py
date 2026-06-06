from langchain_experimental.text_splitter import SemanticChunker as LangChainSemanticChunker
from langchain_openai import OpenAIEmbeddings

from fleet_recruiter_ai_agent.config import settings


class SemanticChunker:
    """Use OpenAI embedding similarity to split source text at topic changes.

    Memory ingestion needs coherent text segments before Redis persistence and hybrid
    indexing. This wrapper owns LangChain configuration and exposes only plain strings
    so the rest of the memory system does not depend on LangChain document types.
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
