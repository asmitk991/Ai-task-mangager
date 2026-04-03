import json
import os
from typing import Any, Dict, List

from google import genai
from google.genai import types
from dotenv import load_dotenv

from schemas.task import ParsedTaskSchema
from utils.exceptions import GeminiAPIError, GeminiResponseError

load_dotenv()

class GeminiTaskParser:
    def __init__(self) -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        self.max_retries = int(os.getenv("GEMINI_MAX_RETRIES", "3"))

        if not api_key:
            raise GeminiAPIError("GEMINI_API_KEY is not configured. Please add it to your .env file.")

        # Initialize the new google-genai client
        self.client = genai.Client(api_key=api_key)

    def parse_tasks(self, text: str) -> List[ParsedTaskSchema]:
        last_error = "Unknown parser failure."

        for attempt in range(1, self.max_retries + 1):
            try:
                raw_content = self._call_gemini(text)
                payload = self._extract_json(raw_content)
                tasks = self._validate_payload(payload)
                if not tasks:
                    raise GeminiResponseError("Gemini returned an empty task list.")
                return tasks
            except (json.JSONDecodeError, GeminiResponseError, ValueError) as exc:
                last_error = str(exc)
                if attempt == self.max_retries:
                    break

        raise GeminiResponseError(f"Unable to parse Gemini response after retries: {last_error}")

    def _call_gemini(self, text: str) -> str:
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
            response = self.client.models.generate_content(
                model=self.model,
                contents=[text],
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0,
                    max_output_tokens=700,
                    response_mime_type="application/json"
                )
            )
            raw_content = response.text
            print(f"DEBUG: Gemini raw response: {raw_content}")
            if not raw_content:
                raise GeminiResponseError("Gemini returned an empty response.")
            return raw_content
        except Exception as exc:  # noqa: BLE001
            print(f"DEBUG: Gemini API exception: {exc}")
            raise GeminiAPIError(f"Gemini API request failed: {exc}") from exc

    def _extract_json(self, raw_content: str) -> Dict[str, Any]:
        # Handle cases where Gemini might still return markdown or extra text
        raw_content = raw_content.strip()
        if "```json" in raw_content:
            raw_content = raw_content.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_content:
            raw_content = raw_content.split("```")[1].split("```")[0].strip()

        start = raw_content.find("{")
        end = raw_content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            print(f"DEBUG: Failed to find JSON in: {raw_content}")
            raise GeminiResponseError("Gemini response did not contain a valid JSON object.")

        return json.loads(raw_content[start : end + 1])

    def _validate_payload(self, payload: Dict[str, Any]) -> List[ParsedTaskSchema]:
        tasks = payload.get("tasks")
        if not isinstance(tasks, list):
            raise GeminiResponseError("Gemini payload must contain a tasks array.")
        return [ParsedTaskSchema.model_validate(item) for item in tasks]
