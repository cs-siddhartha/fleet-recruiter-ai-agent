from enum import StrEnum

from pydantic import BaseModel, Field


class EvaluationStatus(StrEnum):
    """Lifecycle states for a candidate evaluation."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


class EvaluationStage(StrEnum):
    """Pipeline stages reported to the frontend while an evaluation runs."""

    QUEUED = "queued"
    PARSING_RESUME = "parsing_resume"
    ANALYZING = "analyzing"
    COMPLETE = "complete"
    ERROR = "error"


class EvaluationRecord(BaseModel):
    """Stored state for one candidate resume evaluation."""

    evaluation_id: str = Field(min_length=1)
    job_id: str = Field(min_length=1)
    file_name: str = Field(min_length=1)
    status: EvaluationStatus
    stage: EvaluationStage
    error: str | None = None
