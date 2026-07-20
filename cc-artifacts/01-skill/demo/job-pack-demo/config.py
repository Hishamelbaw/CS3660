"""Backend selection. This is the ONLY file that decides which LLMBackend
concrete class gets instantiated. It reads a single env var, LLM_BACKEND,
so swapping backends is a config-only change -- no code edits, no
redeploy of business logic.
"""
import os

from llm_backends.hosted_ollama import HostedOllamaBackend
from llm_backends.claude_api import ClaudeAPIBackend

_REGISTRY = {
    "hosted_ollama": HostedOllamaBackend,
    "claude_api": ClaudeAPIBackend,
}


def get_llm_backend():
    name = os.environ.get("LLM_BACKEND", "hosted_ollama")
    try:
        backend_cls = _REGISTRY[name]
    except KeyError:
        raise ValueError(
            f"Unknown LLM_BACKEND={name!r}. Available: {list(_REGISTRY)}"
        )
    return backend_cls()
