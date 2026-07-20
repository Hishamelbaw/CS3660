import pytest

from app.config import get_llm_backend
from app.llm_backends.claude_api import ClaudeAPIBackend
from app.llm_backends.hosted_ollama import HostedOllamaBackend
from app.llm_backends.local_ollama import LocalOllamaBackend


@pytest.fixture(autouse=True)
def backend_credentials(monkeypatch):
    """Dummy credentials so each backend can be constructed without a real .env.

    Construction never makes a network call (generate() does), so this stays
    entirely offline.
    """
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-anthropic-key")
    monkeypatch.setenv("CLASS_OLLAMA_BASE_URL", "http://class-ollama.test")
    monkeypatch.setenv("CLASS_OLLAMA_MODEL", "test-model")
    monkeypatch.setenv("LOCAL_OLLAMA_MODEL", "test-model")


@pytest.mark.parametrize(
    "backend_name, expected_class",
    [
        ("hosted_ollama", HostedOllamaBackend),
        ("claude_api", ClaudeAPIBackend),
        ("local_ollama", LocalOllamaBackend),
    ],
)
def test_get_llm_backend_returns_expected_class(monkeypatch, backend_name, expected_class):
    monkeypatch.setenv("LLM_BACKEND", backend_name)
    backend = get_llm_backend()
    assert isinstance(backend, expected_class)


def test_get_llm_backend_defaults_to_hosted_ollama(monkeypatch):
    monkeypatch.delenv("LLM_BACKEND", raising=False)
    backend = get_llm_backend()
    assert isinstance(backend, HostedOllamaBackend)


def test_get_llm_backend_rejects_unknown_backend(monkeypatch):
    monkeypatch.setenv("LLM_BACKEND", "not_a_real_backend")
    with pytest.raises(ValueError, match="Unknown LLM_BACKEND"):
        get_llm_backend()
