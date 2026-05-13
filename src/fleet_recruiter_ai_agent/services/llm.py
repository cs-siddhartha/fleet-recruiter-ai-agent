from typing import TypeVar

from openai import OpenAI
from pydantic import BaseModel

from fleet_recruiter_ai_agent.config import settings


SchemaT = TypeVar("SchemaT", bound=BaseModel)


class LLMClient:
    """OpenAI client wrapper for Pydantic structured outputs."""

    def __init__(self) -> None:
        """Initialize the OpenAI client or fail when no API key is configured."""

        if settings.openai_api_key is None:
            raise RuntimeError("OPENAI_API_KEY is required.")
        self._client = OpenAI(api_key=settings.openai_api_key.get_secret_value())

    def parse(self, system_prompt: str, user_prompt: str, schema: type[SchemaT]) -> SchemaT:
        response = self._client.responses.parse(
            model=settings.openai_model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            text_format=schema,
        )
        parsed = response.output_parsed
        if parsed is None:
            raise RuntimeError("OpenAI did not return parsed structured output.")
        return parsed
