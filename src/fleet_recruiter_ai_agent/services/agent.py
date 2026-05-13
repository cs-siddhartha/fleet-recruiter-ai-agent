from typing import Any

from pydantic import BaseModel, Field

from fleet_recruiter_ai_agent.schemas.analysis import CandidateScorecard
from fleet_recruiter_ai_agent.schemas.jobs import JobDetail
from fleet_recruiter_ai_agent.schemas.resume import ParsedResume
from fleet_recruiter_ai_agent.services.llm import LLMClient
from fleet_recruiter_ai_agent.tools.github_enrichment import GitHubEnrichmentInput, enrich_github_profiles
from fleet_recruiter_ai_agent.tools.jd_analysis import JDAnalysisInput, analyze_jd
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
1. Call analyze_jd.
2. Call analyze_resume.
3. If resume analysis includes public GitHub links, call enrich_github_profiles.
4. Call evaluate_scorecard.
5. Return only the final CandidateScorecard JSON.
Do not invent a pass/fail decision.
"""


def run_recruiter_agent(job: JobDetail, parsed_resume: ParsedResume, llm_client: LLMClient) -> CandidateScorecard:
    """Run the tool-calling recruiter agent for one job and parsed resume."""

    state: dict[str, Any] = {"github_profiles": []}

    def handle_analyze_jd(_: dict[str, Any]) -> BaseModel:
        """Execute JD analysis against the fixed backend-owned job."""

        state["jd_analysis"] = analyze_jd(JDAnalysisInput(job=job), llm_client)
        return state["jd_analysis"]

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

        if "jd_analysis" not in state or "resume_analysis" not in state:
            raise RuntimeError("JD and resume analysis must run before scorecard evaluation.")
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
            "Evaluate this candidate against the selected backend-owned job.\n\n"
            f"Job:\n{job.model_dump_json()}\n\n"
            f"Parsed resume:\n{parsed_resume.model_dump_json()}"
        ),
        tools=[
            _tool("analyze_jd", "Analyze the selected backend-owned JD.", EmptyToolInput),
            _tool("analyze_resume", "Analyze the parsed candidate resume.", EmptyToolInput),
            _tool(
                "enrich_github_profiles",
                "Fetch public GitHub profile and repo signals for resume links.",
                GitHubToolInput,
            ),
            _tool("evaluate_scorecard", "Generate the final explainable candidate scorecard.", EmptyToolInput),
        ],
        tool_handlers={
            "analyze_jd": handle_analyze_jd,
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
