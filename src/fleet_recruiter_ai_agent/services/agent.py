from typing import Any

from pydantic import BaseModel, Field

from fleet_recruiter_ai_agent.schemas.analysis import CandidateScorecard
from fleet_recruiter_ai_agent.schemas.jobs import JobDetail
from fleet_recruiter_ai_agent.schemas.resume import ParsedResume
from fleet_recruiter_ai_agent.services.llm import LLMClient
from fleet_recruiter_ai_agent.services.memory import JobMemoryService
from fleet_recruiter_ai_agent.tools.github_enrichment import GitHubEnrichmentInput, enrich_github_profiles
from fleet_recruiter_ai_agent.tools.resume_analysis import ResumeAnalysisInput, analyze_resume
from fleet_recruiter_ai_agent.tools.scorecard_evaluation import ScorecardEvaluationInput, evaluate_scorecard


class EmptyToolInput(BaseModel):
    """Empty input schema for tools that use fixed evaluation context."""


class GitHubToolInput(BaseModel):
    """Input schema for selecting public links to enrich."""

    urls: list[str] = Field(default_factory=list)


SYSTEM_PROMPT = """
You are an AI recruiter agent. Use the available tools before answering.
Required flow:
1. The job description analysis has already been loaded from memory.
2. Call analyze_resume.
3. If resume analysis includes public GitHub links, call enrich_github_profiles.
4. Call evaluate_scorecard.
5. Return only the final CandidateScorecard JSON.
Do not invent a pass/fail decision.
"""


def run_recruiter_agent(
    job: JobDetail,
    parsed_resume: ParsedResume,
    llm_client: LLMClient,
    memory_service: JobMemoryService,
) -> CandidateScorecard:
    """Load job memory first, then run candidate-specific agent tools."""

    job_memory = memory_service.get_or_analyze(job, llm_client)
    state: dict[str, Any] = {
        "jd_analysis": job_memory.analysis,
        "github_profiles": [],
    }

    def handle_analyze_resume(_: dict[str, Any]) -> BaseModel:
        """Execute resume analysis against the parsed uploaded resume."""

        state["resume_analysis"] = analyze_resume(ResumeAnalysisInput(parsed_resume=parsed_resume), llm_client)
        return state["resume_analysis"]

    def handle_enrich_github_profiles(arguments: dict[str, Any]) -> list[BaseModel]:
        """Execute GitHub enrichment for agent-selected public links."""

        payload = GitHubToolInput.model_validate(arguments)
        profiles = enrich_github_profiles(GitHubEnrichmentInput(urls=payload.urls))
        state["github_profiles"] = profiles
        return profiles

    def handle_evaluate_scorecard(_: dict[str, Any]) -> BaseModel:
        """Execute final scorecard generation using prior tool outputs."""

        if "resume_analysis" not in state:
            raise RuntimeError("Resume analysis must run before scorecard evaluation.")
        scorecard = evaluate_scorecard(
            ScorecardEvaluationInput(
                job=job,
                jd_analysis=state["jd_analysis"],
                resume_analysis=state["resume_analysis"],
                github_profiles=state["github_profiles"],
            ),
            llm_client,
        )
        state["scorecard"] = scorecard
        return scorecard

    return llm_client.run_tool_agent(
        SYSTEM_PROMPT,
        (
            "Evaluate this candidate using the job analysis loaded from memory.\n\n"
            f"Job:\n{job.model_dump_json()}\n\n"
            f"Stored JD analysis:\n{job_memory.analysis.model_dump_json()}\n\n"
            f"Parsed resume:\n{parsed_resume.model_dump_json()}"
        ),
        tools=[
            _tool("analyze_resume", "Analyze the parsed candidate resume.", EmptyToolInput),
            _tool(
                "enrich_github_profiles",
                "Fetch public GitHub profile and repo signals for resume links.",
                GitHubToolInput,
            ),
            _tool("evaluate_scorecard", "Generate the final explainable candidate scorecard.", EmptyToolInput),
        ],
        tool_handlers={
            "analyze_resume": handle_analyze_resume,
            "enrich_github_profiles": handle_enrich_github_profiles,
            "evaluate_scorecard": handle_evaluate_scorecard,
        },
        final_schema=CandidateScorecard,
    )


def _tool(name: str, description: str, schema: type[BaseModel]) -> dict[str, Any]:
    """Build an OpenAI function tool definition from a Pydantic schema."""

    return {
        "type": "function",
        "function": {
            "name": name,
            "description": description,
            "parameters": schema.model_json_schema(),
        },
    }
