from pydantic import BaseModel, Field


class GitHubRepositorySignal(BaseModel):
    """Public repository signal used during candidate evaluation."""

    name: str = Field(min_length=1)
    url: str = Field(min_length=1)
    description: str | None = None
    stars: int = Field(ge=0)
    forks: int = Field(ge=0)
    language: str | None = None


class GitHubProfileSignal(BaseModel):
    """Public GitHub profile signal extracted from a resume URL."""

    username: str = Field(min_length=1)
    profile_url: str = Field(min_length=1)
    public_repos: int = Field(ge=0)
    followers: int = Field(ge=0)
    repositories: list[GitHubRepositorySignal] = Field(default_factory=list)
