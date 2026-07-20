"""Claude API backend -- second Strategy implementation."""
import os
import anthropic

from .base import LLMBackend


class ClaudeAPIBackend(LLMBackend):
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    def generate(self, prompt: str, *, max_tokens: int = 1024) -> str:
        msg = self.client.messages.create(
            model="claude-sonnet-5",
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return msg.content[0].text
