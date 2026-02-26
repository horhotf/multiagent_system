from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import httpx

from app.config import settings

ROOT_DIR = Path(__file__).resolve().parents[2]
PROMPTS_DIR = ROOT_DIR / "prompts"


class LLMClient:
    def __init__(self) -> None:
        self.base_url = settings.llm_base_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model

    @staticmethod
    def _render_template(template: str, variables: dict[str, Any] | None = None) -> str:
        result = template
        for key, value in (variables or {}).items():
            result = result.replace("{{" + key + "}}", str(value))
        return result

    def call_prompt(
        self,
        prompt_file: str,
        variables: dict[str, Any],
        user_input: str,
        json_only: bool = False,
    ) -> str:
        system_prompt = (PROMPTS_DIR / prompt_file).read_text(encoding="utf-8")
        system_prompt = self._render_template(system_prompt, variables)
        if json_only:
            system_prompt += "\n\nReturn JSON only. No markdown."

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
            "temperature": 0.1,
        }
        if json_only:
            payload["response_format"] = {"type": "json_object"}

        headers = {"Authorization": f"Bearer {self.api_key}"}
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        return data["choices"][0]["message"]["content"]

    def call_json(
        self,
        prompt_file: str,
        variables: dict[str, Any],
        user_input: str,
    ) -> dict[str, Any]:
        raw = self.call_prompt(prompt_file, variables, user_input, json_only=True)
        return json.loads(raw)


llm_client = LLMClient()
