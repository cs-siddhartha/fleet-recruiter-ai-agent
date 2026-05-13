import json
from collections.abc import Callable
from typing import Any, TypeVar

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
        """Call OpenAI once and parse the response into a Pydantic schema."""

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

    def run_tool_agent(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[dict[str, Any]],
        tool_handlers: dict[str, Callable[[dict[str, Any]], BaseModel | list[BaseModel]]],
        final_schema: type[SchemaT],
        max_steps: int = 8,
    ) -> SchemaT:
        """Run a tool-calling loop and validate the final answer with Pydantic."""

        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        for _ in range(max_steps):
            response = self._client.chat.completions.create(
                model=settings.openai_model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                response_format={"type": "json_object"},
            )
            message = response.choices[0].message
            messages.append(message.model_dump(exclude_none=True))

            if not message.tool_calls:
                if message.content is None:
                    raise RuntimeError("OpenAI returned no final scorecard content.")
                return final_schema.model_validate_json(message.content)

            for tool_call in message.tool_calls:
                handler = tool_handlers.get(tool_call.function.name)
                if handler is None:
                    raise RuntimeError(f"Unknown tool requested: {tool_call.function.name}")
                arguments = json.loads(tool_call.function.arguments or "{}")
                result = handler(arguments)
                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": _json_result(result),
                    }
                )

        raise RuntimeError("OpenAI agent exceeded maximum tool-call steps.")


def _json_result(result: BaseModel | list[BaseModel]) -> str:
    """Serialize a Pydantic tool result for the next agent turn."""

    if isinstance(result, list):
        return json.dumps([item.model_dump(mode="json") for item in result])
    return result.model_dump_json()
