from typing import Any

import requests

from ai_research_studio.llm.base import BaseLLMClient
from ai_research_studio.settings import settings


class OpenAICompatibleClient(BaseLLMClient):
    def __init__(
        self,
        api_key: str,
        base_url: str,
        model: str,
        timeout: int,
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def generate(self, messages: list[dict[str, str]]) -> str | None:
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout,
            )
            response.raise_for_status()
            data = response.json()

            ##print("LLM raw response keys:", data.keys())

            content = data["choices"][0]["message"]["content"].strip()
            return content or None

        except Exception as e:
            print("LLM request failed:", repr(e))
            try:
                print("LLM response text:", response.text)  # type: ignore[name-defined]
            except Exception:
                pass
            return None


def build_llm_client() -> BaseLLMClient | None:
    if not settings.openai_api_key:
        print("LLM disabled: missing OPENAI_API_KEY")
        return None

    if not settings.use_llm_summary:
        print("LLM disabled: USE_LLM_SUMMARY is false")
        return None

    if settings.llm_provider != "openai_compatible":
        print(f"LLM disabled: unsupported provider {settings.llm_provider}")
        return None

    return OpenAICompatibleClient(
        api_key=settings.openai_api_key,
        base_url=settings.openai_base_url,
        model=settings.openai_model,
        timeout=settings.llm_timeout,
    )