from threading import Lock

from fleet_recruiter_ai_agent.schemas.evaluations import (
    EvaluationRecord,
    EvaluationStage,
    EvaluationStatus,
)


class EvaluationStore:
    """Thread-safe in-memory store for candidate evaluation state."""

    def __init__(self) -> None:
        """Initialize an empty evaluation store."""

        self._records: dict[str, EvaluationRecord] = {}
        # FastAPI can serve upload and polling requests concurrently, so this keeps
        # in-memory dictionary reads/writes from racing in the local v1 store.
        self._lock = Lock()

    def create(self, record: EvaluationRecord) -> EvaluationRecord:
        """Store a new evaluation record and return it."""

        with self._lock:
            self._records[record.evaluation_id] = record
            return record

    def get(self, evaluation_id: str) -> EvaluationRecord | None:
        """Return an evaluation by id, or None when it does not exist."""

        with self._lock:
            return self._records.get(evaluation_id)

    def update_stage(self, evaluation_id: str, stage: EvaluationStage) -> EvaluationRecord:
        """Update an evaluation stage and mark it as running."""

        with self._lock:
            record = self._records[evaluation_id].model_copy(
                update={"status": EvaluationStatus.RUNNING, "stage": stage}
            )
            self._records[evaluation_id] = record
            return record

    def fail(self, evaluation_id: str, error: str) -> EvaluationRecord:
        """Mark an evaluation as failed with a user-readable error."""

        with self._lock:
            record = self._records[evaluation_id].model_copy(
                update={"status": EvaluationStatus.ERROR, "stage": EvaluationStage.ERROR, "error": error}
            )
            self._records[evaluation_id] = record
            return record

    def save_resume_text(self, evaluation_id: str, resume_text: str) -> EvaluationRecord:
        """Store parsed resume text on an evaluation."""

        with self._lock:
            record = self._records[evaluation_id].model_copy(
                update={"status": EvaluationStatus.RUNNING, "resume_text": resume_text}
            )
            self._records[evaluation_id] = record
            return record

    def complete(self, evaluation_id: str, result) -> EvaluationRecord:
        """Store the final scorecard and mark an evaluation complete."""

        with self._lock:
            record = self._records[evaluation_id].model_copy(
                update={"status": EvaluationStatus.COMPLETE, "stage": EvaluationStage.COMPLETE, "result": result}
            )
            self._records[evaluation_id] = record
            return record


evaluation_store = EvaluationStore()
