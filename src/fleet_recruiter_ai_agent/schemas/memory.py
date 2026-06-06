from pydantic import BaseModel, Field

from fleet_recruiter_ai_agent.schemas.analysis import JDAnalysis


class JobMemory(BaseModel):
    """Represent the reusable analysis and source context for one job.

    Candidate evaluations already identify the target job, so retrieval only needs an
    exact ``job_id`` lookup. This record keeps the original description and structured
    analysis together without retaining candidate information.
    """

    job_id: str = Field(min_length=1)
    job_title: str = Field(min_length=1)
    job_description: str = Field(min_length=1)
    analysis: JDAnalysis

    # TODO(platform): Add semantic chunks and OpenAI vectors when candidates can upload
    # a resume without selecting a job. That extension will search across indexed jobs
    # to recommend matches instead of retrieving one known job by its exact ID.
