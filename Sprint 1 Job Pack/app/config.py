import os

from dotenv import load_dotenv

from app.llm_backends.base import LLMBackend
from app.llm_backends.claude_api import ClaudeAPIBackend
from app.llm_backends.hosted_ollama import HostedOllamaBackend
from app.llm_backends.local_ollama import LocalOllamaBackend

load_dotenv()

_BACKENDS = {
    "hosted_ollama": HostedOllamaBackend,
    "claude_api": ClaudeAPIBackend,
    "local_ollama": LocalOllamaBackend,
}


def get_llm_backend() -> LLMBackend:
    """Strategy factory: reads LLM_BACKEND from the environment and returns the matching backend.

    No other module should import a concrete backend directly — this is the single
    place that decides which LLMBackend implementation is active.
    """
    name = os.environ.get("LLM_BACKEND", "hosted_ollama")
    try:
        backend_cls = _BACKENDS[name]
    except KeyError:
        raise ValueError(f"Unknown LLM_BACKEND: {name!r}. Choose from {list(_BACKENDS)}.")
    return backend_cls()
