from pydantic import BaseModel

from fleet_recruiter_ai_agent.schemas.analysis import ResumeAnalysis
from fleet_recruiter_ai_agent.schemas.resume import ParsedResume
from fleet_recruiter_ai_agent.services.llm import LLMClient


class ResumeAnalysisInput(BaseModel):
    """Input payload for analyzing parsed resume text."""

    parsed_resume: ParsedResume


def analyze_resume(payload: ResumeAnalysisInput, llm_client: LLMClient) -> ResumeAnalysis:
    """Extract structured candidate signals from parsed resume text with OpenAI."""

    return llm_client.parse(
        "Analyze candidate resumes into structured recruiting evidence. Focus on concrete impact, projects, links, and risks.",
        f"File name: {payload.parsed_resume.file_name}\n\nResume markdown:\n{payload.parsed_resume.text}",
        ResumeAnalysis,
    )
