import json
import os
from typing import Any, Dict, List

from anthropic import Anthropic
from dotenv import load_dotenv

from schemas.task import ParsedTaskSchema
from utils.exceptions import ClaudeAPIError, ClaudeResponseError


load_dotenv()


class ClaudeTaskParser:
    def __init__(self) -> None:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        self.model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-latest")
        self.max_retries = int(os.getenv("CLAUDE_MAX_RETRIES", "3"))

        if not api_key:
            raise ClaudeAPIError("ANTHROPIC_API_KEY is not configured.")

        self.client = Anthropic(api_key=api_key)

    def parse_tasks(self, text: str) -> List[ParsedTaskSchema]:
        last_error = "Unknown parser failure."

        for attempt in range(1, self.max_retries + 1):
            try:
                raw_content = self._call_claude(text)
                payload = self._extract_json(raw_content)
                tasks = self._validate_payload(payload)
                if not tasks:
                    raise ClaudeResponseError("Claude returned an empty task list.")
                return tasks
            except (json.JSONDecodeError, ClaudeResponseError, ValueError) as exc:
                last_error = str(exc)
                if attempt == self.max_retries:
                    break

        raise ClaudeResponseError(f"Unable to parse Claude response after retries: {last_error}")

    def _call_claude(self, text: str) -> str:
        system_prompt = (
            "You convert messy user task notes into strict JSON. "
            "Return JSON only with this exact shape: "
            '{"tasks":[{"title":"string","description":"string|null","deadline":"YYYY-MM-DD|null",'
            '"priority":"low|medium|high","category":"string","status":"pending|in_progress|done"}]}. '
            "Do not include markdown fences or commentary. "
            "If a field is unknown, use null for deadline/description and sensible defaults for priority, "
            'category, and status. Split compound requests into multiple tasks when appropriate.'
        )

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=700,
                temperature=0,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Parse this task input into JSON:\n{text}",
                    }
                ],
            )
        except Exception as exc:  # noqa: BLE001
            raise ClaudeAPIError(f"Claude API request failed: {exc}") from exc

        chunks = []
        for block in response.content:
            block_text = getattr(block, "text", None)
            if block_text:
                chunks.append(block_text)

        raw_content = "".join(chunks).strip()
        if not raw_content:
            raise ClaudeResponseError("Claude returned an empty response.")
        return raw_content

    def _extract_json(self, raw_content: str) -> Dict[str, Any]:
        if raw_content.startswith("```"):
            stripped = raw_content.strip("`")
            raw_content = stripped.replace("json\n", "", 1).strip()

        start = raw_content.find("{")
        end = raw_content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise ClaudeResponseError("Claude response did not contain a valid JSON object.")

        return json.loads(raw_content[start : end + 1])

    def _validate_payload(self, payload: Dict[str, Any]) -> List[ParsedTaskSchema]:
        tasks = payload.get("tasks")
        if not isinstance(tasks, list):
            raise ClaudeResponseError("Claude payload must contain a tasks array.")
        return [ParsedTaskSchema.model_validate(item) for item in tasks]
