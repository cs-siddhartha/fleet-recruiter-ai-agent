from pydantic import BaseModel

from fleet_recruiter_ai_agent.schemas.analysis import JDAnalysis
from fleet_recruiter_ai_agent.schemas.jobs import JobDetail
from fleet_recruiter_ai_agent.services.llm import LLMClient


class JDAnalysisInput(BaseModel):
    """Input payload for analyzing a backend-owned job description."""

    job: JobDetail


def analyze_jd(payload: JDAnalysisInput, llm_client: LLMClient) -> JDAnalysis:
    """Extract structured requirements from a job description with OpenAI."""

    return llm_client.parse(
        "Analyze job descriptions into structured recruiting requirements. Return concise evidence-focused fields.",
        f"Job title: {payload.job.title}\n\nJob description:\n{payload.job.job_description}",
        JDAnalysis,
    )
