import tempfile
from pathlib import Path

import pymupdf4llm
from pydantic import BaseModel, Field

from fleet_recruiter_ai_agent.schemas.resume import ParsedResume


class PDFExtractionInput(BaseModel):
    """Input payload for extracting text from a PDF resume."""

    file_name: str = Field(min_length=1)
    content: bytes = Field(min_length=1)


def normalize_markdown_output(markdown_output: str | list[dict]) -> str:
    """Normalize PyMuPDF4LLM output into one Markdown document string."""

    if isinstance(markdown_output, list):
        return "\n".join(str(page.get("text", "")) for page in markdown_output).strip()
    return markdown_output.strip()


def extract_resume_text(payload: PDFExtractionInput) -> ParsedResume:
    """Extract LLM-friendly Markdown text from a PDF resume.

    Raises:
        ValueError: If the PDF cannot be converted or contains no text.
    """

    with tempfile.NamedTemporaryFile(suffix=".pdf") as pdf_file:
        pdf_file.write(payload.content)
        pdf_file.flush()
        markdown_text = normalize_markdown_output(pymupdf4llm.to_markdown(Path(pdf_file.name)))

    if not markdown_text:
        raise ValueError("Resume PDF did not contain extractable text.")

    return ParsedResume(file_name=payload.file_name, text=markdown_text)
