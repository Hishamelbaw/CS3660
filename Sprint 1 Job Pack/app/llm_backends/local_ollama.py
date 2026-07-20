import os

import requests

from app.llm_backends.base import LLMBackend


class LocalOllamaBackend(LLMBackend):
    """Talks to a locally-running Ollama instance (native /api/generate endpoint)."""

    def __init__(self) -> None:
        self.base_url = os.environ.get("LOCAL_OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
        self.model = os.environ["LOCAL_OLLAMA_MODEL"]

    def generate(self, prompt: str) -> str:
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        response.raise_for_status()
        return response.json()["response"]
