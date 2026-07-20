import os

import requests

from app.llm_backends.base import LLMBackend


class HostedOllamaBackend(LLMBackend):
    """Talks to the class-hosted Ollama instance (native /api/generate endpoint)."""

    def __init__(self) -> None:
        self.base_url = os.environ["CLASS_OLLAMA_BASE_URL"].rstrip("/")
        self.api_key = os.environ.get("CLASS_OLLAMA_API_KEY", "")
        self.model = os.environ["CLASS_OLLAMA_MODEL"]

    def generate(self, prompt: str) -> str:
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            headers=headers,
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"]
