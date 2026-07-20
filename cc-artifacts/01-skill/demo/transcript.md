# Demonstration: `/swap-llm-backend`

Scaffold used for this run lives in `demo/job-pack-demo/` — a minimal
stand-in for the Job Pack app with the mandatory Strategy-pattern LLM
layer, starting with only the `hosted_ollama` backend.

## Starting state

```
job-pack-demo/
├── config.py              # the only file allowed to import a concrete backend
├── main.py                # business logic — must never import a backend directly
├── .env.example
└── llm_backends/
    ├── base.py             # LLMBackend Strategy interface
    └── hosted_ollama.py    # only backend implemented so far
```

`config.py` at baseline:

```python
_REGISTRY = {
    "hosted_ollama": HostedOllamaBackend,
}
```

## Invocation

```
> /swap-llm-backend add the claude_api backend
```

## Claude Code's response (following the skill's steps)

> Located the Strategy interface at `llm_backends/base.py`
> (`LLMBackend.generate`). Located the registry/factory at `config.py` —
> confirmed it's the only file importing concrete backend classes;
> `main.py` only imports `get_llm_backend`, good.
>
> Scaffolding `llm_backends/claude_api.py` implementing `LLMBackend`,
> pulling `ANTHROPIC_API_KEY` from `os.environ` (never hardcoded).
> Registering it in `config.py` with one import + one dict entry. Adding
> a placeholder `ANTHROPIC_API_KEY=your-key-here` line to `.env.example`.
> Not touching `main.py`.
>
> Running the config-only-swap check now.

## What actually got written

`llm_backends/claude_api.py` (new file):

```python
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
```

`config.py` diff (via `git diff HEAD~1 HEAD -- config.py`):

```diff
 import os

 from llm_backends.hosted_ollama import HostedOllamaBackend
+from llm_backends.claude_api import ClaudeAPIBackend

 _REGISTRY = {
     "hosted_ollama": HostedOllamaBackend,
+    "claude_api": ClaudeAPIBackend,
 }
```

`main.py` diff (via `git diff HEAD~1 HEAD -- main.py`):

```
(no output — zero changes)
```

Full changeset (`git diff --stat HEAD~1 HEAD`):

```
 .env.example               |  3 +++
 config.py                  |  2 ++
 llm_backends/claude_api.py | 18 ++++++++++++++++++
 3 files changed, 23 insertions(+)
```

## Step 5 — verifying the config-only swap

With both backends now registered, switching which one Job Pack uses is
a one-line `.env` edit:

```
$ cp .env.example .env
$ sed -i 's/^LLM_BACKEND=hosted_ollama/LLM_BACKEND=claude_api/' .env
$ git status --porcelain
?? .env
```

Only `.env` (untracked, gitignored) changed. No `.py` file changed to
flip backends — the config-only-swap requirement holds.

## Step 6 — secrets audit

```
$ grep -RnE "sk-[A-Za-z0-9]{10,}|api_key\s*=\s*['\"]" --include=*.py .
(no matches)
$ cat .gitignore
.env
```

No live key present anywhere in tracked files; `.env` is gitignored so
the real `ANTHROPIC_API_KEY` never gets committed. Only `.env.example`
(placeholders) is tracked.

## Summary Claude Code hands back

> Added `llm_backends/claude_api.py` implementing the `LLMBackend`
> Strategy interface. Registered it in `config.py` (1 import, 1 dict
> entry). `main.py` and all other business-logic files: 0 changes.
> Verified switching `LLM_BACKEND` between `hosted_ollama` and
> `claude_api` requires only an `.env` edit — 0 `.py` files change.
> Secrets audit: no live key in any tracked file; `.env` is gitignored,
> `.env.example` holds placeholders only. Ready to paste into the PR
> description.
