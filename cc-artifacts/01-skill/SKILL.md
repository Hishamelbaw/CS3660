---
name: swap-llm-backend
description: Guided refactor for the Job Pack app's LLM layer. Adds a new LLMBackend Strategy implementation (hosted class Ollama, Claude API, or raw local Ollama), registers it so backend selection stays a config-only change, and audits that no API key is hardcoded or committed. Use this when adding a backend for the first time, verifying that swapping backends requires zero code edits, or reviewing a teammate's backend PR before merge.
tools: Read, Write, Edit, Grep, Glob, Bash
---

# swap-llm-backend

## Purpose

The Job Pack sprint requires the LLM layer to be swappable via the Strategy
pattern across at least two backends (hosted class Ollama, Claude API, raw
local Ollama), with switching enforced as a **config-only change** — no
code edits when a user flips `LLM_BACKEND` in `.env`. This skill automates
the two things that go wrong in practice: a new backend gets added but
business logic (`main.py`, the resume/cover-letter/infographic generators)
accidentally imports it directly, and secrets get hardcoded or slip into a
commit.

## When to invoke

Invoke this skill when:
- Adding a backend implementation that doesn't exist yet (e.g., "add the
  Claude API backend").
- Verifying that an existing set of backends can be swapped with only an
  `.env` change (pre-demo sanity check).
- Reviewing a teammate's PR that touches `llm_backends/` or `config.py`.

## Steps

1. **Locate the Strategy interface.** Find the abstract base class (e.g.
   `llm_backends/base.py`) that all backends implement. If it doesn't
   exist yet, this is a signal the Strategy pattern isn't in place —
   stop and create it first (single `generate(prompt, **kwargs)` method
   is enough for Job Pack's needs).

2. **Find the registry / factory.** Find the single place (typically
   `config.py`) that maps an env var (`LLM_BACKEND`) to a concrete
   backend class. This is the only file allowed to import concrete
   backend classes. If business logic files import a concrete backend
   directly, flag it — that breaks the config-only-swap requirement.

3. **Scaffold the new backend.**
   - Create `llm_backends/<name>.py` implementing the Strategy interface.
   - Pull all credentials from `os.environ`, never hardcode them.
   - Add the corresponding var(s) to `.env.example` with placeholder
     values only (never a real key).

4. **Register, don't rewire.** Add one import + one dict entry to the
   registry file. Do not touch `main.py` or any other business-logic
   file. If a change to those files seems necessary, that's a design
   smell — the Strategy interface is probably leaking backend-specific
   details and needs tightening instead.

5. **Verify config-only swap.** Run (or instruct the user to run):
   ```
   git diff --stat <before> <after>
   ```
   and confirm business-logic files (main.py, the generators) show zero
   changes. Then confirm switching backends is just editing `LLM_BACKEND`
   in `.env` — no redeploy of code, only a restart/re-read of env.

6. **Secrets audit.** Before finishing, grep the diff and `.env.example`
   for anything that looks like a live key (`sk-`, long hex/base64
   strings, etc.) and confirm `.env` (not `.env.example`) is listed in
   `.gitignore`. Flag anything that isn't a placeholder.

7. **Summarize.** Report which files changed, confirm business logic was
   untouched, and confirm no secret was committed. This summary is what
   gets pasted into the team's PR description or demo notes.

## Non-goals

This skill does not choose which backend to add — the user specifies
that. It does not manage deployment (Netlify/uvucs.org) or persistence
(draft storage); those are separate concerns in the Job Pack Perfect
Framework checklist.
