from pydantic import BaseModel

from fleet_recruiter_ai_agent.schemas.analysis import CandidateScorecard, JDAnalysis, ResumeAnalysis
from fleet_recruiter_ai_agent.schemas.jobs import JobDetail
from fleet_recruiter_ai_agent.services.llm import LLMClient


class ScorecardEvaluationInput(BaseModel):
    """Input payload for evaluating a candidate against one selected job."""

    job: JobDetail
    jd_analysis: JDAnalysis
    resume_analysis: ResumeAnalysis


def evaluate_scorecard(payload: ScorecardEvaluationInput, llm_client: LLMClient) -> CandidateScorecard:
    """Generate an explainable candidate scorecard with OpenAI."""

    return llm_client.parse(
        (
            "Evaluate a candidate against a job. Do not produce a hard pass/fail. "
            "Return an explainable scorecard with comments, evidence, risks, and interview questions."
        ),
        payload.model_dump_json(),
        CandidateScorecard,
    )
