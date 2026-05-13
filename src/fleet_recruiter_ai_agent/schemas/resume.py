from pydantic import BaseModel, Field


class ParsedResume(BaseModel):
    """Text extracted from a candidate resume PDF."""

    file_name: str = Field(min_length=1)
    text: str = Field(min_length=1)
