"""Strategy interface for LLM backends used by the Job Pack pipeline.

Every concrete backend (hosted class Ollama, Claude API, raw local Ollama)
implements this interface. The rest of the app (config.py, main.py, the
resume/cover-letter/infographic generators) only ever talks to this
interface, never to a concrete backend directly.
"""
from abc import ABC, abstractmethod


class LLMBackend(ABC):
    @abstractmethod
    def generate(self, prompt: str, *, max_tokens: int = 1024) -> str:
        """Send prompt to the backend and return the completion text."""
        raise NotImplementedError
