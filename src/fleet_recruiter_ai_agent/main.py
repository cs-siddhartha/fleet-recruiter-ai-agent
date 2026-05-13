from pydantic import ValidationError

from .models import CandidateProfile, JobFitResult


def build_sample_result() -> JobFitResult:
    candidate = CandidateProfile(
        full_name="Avery Stone",
        email="avery@example.com",
        years_experience=6,
        skills=["python", "recruiting automation", "llm evaluation"],
        resume_url="https://example.com/resumes/avery-stone",
    )
    return JobFitResult(
        candidate=candidate,
        role="AI Recruiting Engineer",
        match_score=0.86,
        rationale="Strong Python background and applied recruiting automation experience.",
    )


def main() -> None:
    try:
        result = build_sample_result()
    except ValidationError as exc:
        raise SystemExit(f"Invalid sample data: {exc}") from exc

    recommendation = "recommended" if result.is_recommended else "not recommended"
    print(
        f"{result.candidate.full_name} is {recommendation} for "
        f"{result.role} ({result.match_score:.0%})."
    )
