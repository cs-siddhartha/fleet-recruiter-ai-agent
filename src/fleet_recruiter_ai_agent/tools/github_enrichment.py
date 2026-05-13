import re

import httpx
from pydantic import BaseModel, Field

from fleet_recruiter_ai_agent.config import settings
from fleet_recruiter_ai_agent.schemas.enrichment import GitHubProfileSignal, GitHubRepositorySignal


class GitHubEnrichmentInput(BaseModel):
    """Input payload for enriching GitHub profile URLs found in a resume."""

    urls: list[str] = Field(default_factory=list)


GITHUB_USERNAME_PATTERN = re.compile(r"github\.com/([^/\s?#]+)", re.IGNORECASE)


def enrich_github_profiles(payload: GitHubEnrichmentInput) -> list[GitHubProfileSignal]:
    """Fetch public GitHub profile and repository signals for resume URLs."""

    usernames = _extract_usernames(payload.urls)
    with httpx.Client(timeout=settings.public_fetch_timeout_seconds) as client:
        return [_fetch_github_profile(client, username) for username in usernames]


def _extract_usernames(urls: list[str]) -> list[str]:
    """Extract unique GitHub usernames from public profile or repository URLs."""

    usernames: set[str] = set()
    ignored_segments = {"features", "topics", "collections", "orgs", "marketplace", "pricing"}
    for url in urls:
        match = GITHUB_USERNAME_PATTERN.search(url)
        if match and match.group(1).lower() not in ignored_segments:
            usernames.add(match.group(1))
    # A resume can mention the same profile through multiple URLs, like
    # github.com/octocat and github.com/octocat/Hello-World. The set dedupes
    # those, and sorting keeps the enrichment order stable for tests/results.
    return sorted(usernames)


def _fetch_github_profile(client: httpx.Client, username: str) -> GitHubProfileSignal:
    """Fetch one public GitHub profile plus its most-starred repositories."""

    user_response = client.get(f"{settings.github_api_base_url}/users/{username}")
    user_response.raise_for_status()
    user_data = user_response.json()

    repo_response = client.get(
        f"{settings.github_api_base_url}/users/{username}/repos",
        params={"sort": "updated", "per_page": 20},
    )
    repo_response.raise_for_status()
    repositories = sorted(repo_response.json(), key=lambda repo: repo.get("stargazers_count", 0), reverse=True)[:5]

    return GitHubProfileSignal(
        username=username,
        profile_url=f"https://github.com/{username}",
        public_repos=user_data.get("public_repos", 0),
        followers=user_data.get("followers", 0),
        repositories=[
            GitHubRepositorySignal(
                name=repo.get("name", "unknown"),
                url=repo.get("html_url", f"https://github.com/{username}"),
                description=repo.get("description"),
                stars=repo.get("stargazers_count", 0),
                forks=repo.get("forks_count", 0),
                language=repo.get("language"),
            )
            for repo in repositories
        ],
    )
