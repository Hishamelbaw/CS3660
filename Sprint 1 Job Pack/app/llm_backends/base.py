from abc import ABC, abstractmethod


class LLMBackend(ABC):
    """Strategy interface for LLM backends. Every backend takes a prompt and returns text."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        ...
