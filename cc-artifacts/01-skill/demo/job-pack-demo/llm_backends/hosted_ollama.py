"""Default backend: the class-hosted Ollama endpoint."""
import os
import requests

from .base import LLMBackend


class HostedOllamaBackend(LLMBackend):
    def __init__(self):
        self.endpoint = os.environ["CLASS_OLLAMA_ENDPOINT"]
        self.api_key = os.environ["CLASS_OLLAMA_API_KEY"]

    def generate(self, prompt: str, *, max_tokens: int = 1024) -> str:
        resp = requests.post(
            f"{self.endpoint}/api/generate",
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={"model": "llama3", "prompt": prompt, "max_tokens": max_tokens},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()["response"]
