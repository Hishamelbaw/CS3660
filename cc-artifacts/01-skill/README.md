# swap-llm-backend

A Claude Code skill for the Job Pack sprint (CS 3660, Sprint 1).

## What it is

`swap-llm-backend` is a skill — a packaged set of instructions stored as
`SKILL.md` that Claude Code loads on invocation and follows for the rest
of that turn. It is not a hook (hooks fire automatically on lifecycle
events like `PostToolUse`; this skill only runs when explicitly invoked)
and it is not a subagent (it runs inline in the main agentic loop rather
than spawning an isolated context with its own tool budget). Invoking it
is a deliberate act: I type `/swap-llm-backend`, or ask for something the
skill's description matches, and Claude Code decides to load it.

## Why it exists

Job Pack's mandatory technical requirement is that the LLM backend
(hosted class Ollama, Claude API, raw local Ollama) is selectable via the
Strategy pattern, and that switching backends is a **config-only
change** — zero code modification. That's easy to state and easy to
violate in the moment: it's tempting to just import `ClaudeAPIBackend`
directly into `main.py` when you're in a hurry before demo day, which
silently breaks the config-only requirement and costs rubric points.

I add a new backend (or review a teammate's backend PR) multiple times
over the sprint — once per backend, plus review passes. That repetition
is what makes this worth automating rather than doing by hand each time.

## How it helps

The skill enforces the same five-step discipline every time: locate the
Strategy interface, locate the single registry/factory file, scaffold
the new backend against the interface, register it with a one-line diff
instead of rewiring business logic, then run a config-only-swap check
(`git diff --stat` across business-logic files) and a secrets audit
before handing back a summary.

This is an example of **progressive disclosure**: the skill's
`description` field in the YAML frontmatter is the only thing loaded
into context by default, so Claude Code can decide *whether* to invoke
it without paying the cost of the full body. The full step-by-step body
— and the additional context I inject at invocation (which backend to
add, which files are in play) — only enters the **agentic loop**'s
context once the skill actually fires. That keeps the skill cheap to
have "loaded" as an option even when the current task has nothing to do
with the LLM layer.

## When to invoke it

- Adding a backend implementation for the first time (`hosted_ollama`,
  `claude_api`, or `local_ollama`).
- Before demo day, to verify the config-only-swap requirement actually
  holds (not just "should" hold).
- Reviewing a teammate's PR that touches `llm_backends/` or `config.py`.

## Demonstration

See `demo/transcript.md` for a real run: a minimal Job Pack scaffold
with only the `hosted_ollama` backend, the skill's guided addition of a
`claude_api` backend, and the actual `git diff` proving business logic
(`main.py`) was never touched — only the registry gained one import and
one dict entry, plus the new backend file itself. The transcript also
shows the config-only swap: flipping `LLM_BACKEND` in `.env` with zero
`.py` files changing.

## AI use disclosure

Built with Claude Sonnet 5 (Claude Code) per the course AI use policy.
