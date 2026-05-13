from fleet_recruiter_ai_agent.schemas.evaluations import EvaluationStage
from fleet_recruiter_ai_agent.schemas.jobs import JobDetail
from fleet_recruiter_ai_agent.services.agent import run_recruiter_agent
from fleet_recruiter_ai_agent.services.evaluation_store import evaluation_store
from fleet_recruiter_ai_agent.services.llm import LLMClient
from fleet_recruiter_ai_agent.tools.pdf_extraction import PDFExtractionInput, extract_resume_text


def run_evaluation(evaluation_id: str, job: JobDetail, file_name: str, content: bytes) -> None:
    """Run the resume-to-scorecard evaluation pipeline for one uploaded resume."""

    try:
        llm_client = LLMClient()

        evaluation_store.update_stage(evaluation_id, EvaluationStage.PARSING_RESUME)
        parsed_resume = extract_resume_text(PDFExtractionInput(file_name=file_name, content=content))
        evaluation_store.save_resume_text(evaluation_id, parsed_resume.text)

        evaluation_store.update_stage(evaluation_id, EvaluationStage.ANALYZING_JD)
        evaluation_store.update_stage(evaluation_id, EvaluationStage.ANALYZING_RESUME)
        evaluation_store.update_stage(evaluation_id, EvaluationStage.ENRICHING_GITHUB)
        evaluation_store.update_stage(evaluation_id, EvaluationStage.GENERATING_SCORECARD)
        scorecard = run_recruiter_agent(job, parsed_resume, llm_client)
        evaluation_store.complete(evaluation_id, scorecard)
    except Exception as exc:
        evaluation_store.fail(evaluation_id, str(exc))
