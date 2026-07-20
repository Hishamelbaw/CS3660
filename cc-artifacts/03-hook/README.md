# secret-guard

A Claude Code **PreToolUse hook** for the Job Pack sprint (CS 3660,
Sprint 1).

## What it is

`secret-guard.py` is a **PreToolUse hook** — a standalone script
registered in `.claude/settings.json` (see [`settings.json`](settings.json)
in this directory for the exact registration snippet) against the
`PreToolUse` event with a `matcher` of `"Bash"`. It is not a skill and
not a subagent: nobody types `/secret-guard`, and nothing dispatches it
via the Task/Agent tool. It is **event-driven automation** — the
harness runs it automatically, in the background of the agentic loop,
every single time a Bash tool call is about to execute, whether or not
anyone in the conversation remembers it exists.

## The event: PreToolUse, and why that event specifically

Claude Code exposes several hook events (`PreToolUse`, `PostToolUse`,
`UserPromptSubmit`, `Stop`, and others); this hook uses `PreToolUse`.
The distinction that matters here is timing relative to the tool call:

- A **PreToolUse hook** fires *before* the matched tool executes, and
  its exit code changes what happens next: exit 0 lets the call proceed
  untouched, exit 2 **blocks the call entirely** and feeds its stderr
  back to Claude as the reason.
- A **PostToolUse hook** fires *after* the tool has already run — useful
  for logging, formatting, or reacting to a result, but by then a
  `git commit` has already happened. It can tell you a secret got
  committed; it cannot stop it from being committed.

Blocking a bad `git add`/`git commit` before it runs is only possible
from `PreToolUse`. That's the whole reason this artifact is a
`PreToolUse` hook and not a `PostToolUse` one.

## What it does

The hook receives the pending tool call as JSON on stdin (`tool_name`,
`tool_input`, `cwd`, etc.). It only acts when `tool_name` is `"Bash"`
and the command contains `git add` or `git commit`; every other Bash
call passes through untouched. For a matching command it:

1. **Checks for a real `.env` being staged.** For `git add`, it
   resolves which files the command actually targets (explicit paths,
   or everything under `git status --porcelain` for `add .`/`-A`) and
   flags any of them literally named `.env` (not `.env.example` or
   `.env.sample`). For `git commit`, it checks `git diff --cached
   --name-only` for the same.
2. **Scans for secret-shaped literals** — Anthropic/OpenAI-style API
   key prefixes, AWS access key IDs, `Bearer` tokens, and any
   `key`/`secret`/`token`/`password`-named variable assigned a long
   literal — across the content of files about to be staged (`git add`)
   or the actual staged diff (`git diff --cached`, for `git commit`).
   Matches are redacted (`sk-a...3f2d`) before being reported, so the
   hook's own output never leaks the secret it caught.

If either check finds something, the hook **exits 2** and prints a
reason to stderr listing every finding and how to fix it (e.g.
`git restore --staged <file>`). Claude Code surfaces that stderr back
to Claude as the reason the tool call was blocked, so Claude can explain
the block and propose a fix instead of silently retrying the same
command. If nothing is found, it **exits 0** and the command proceeds
exactly as if the hook weren't there.

## Why this matters

Every artifact built this term has cared about the same failure mode
from a different angle: the [`swap-llm-backend`](../01-skill/SKILL.md)
skill's step 6 is a secrets audit run *while adding* a backend, and the
[`vernacular-auditor`](../02-subagent/vernacular-auditor.md) subagent's
Secrets management check *independently audits* whatever ended up on
disk, in its own isolated context, after the fact. Both are valuable,
and both share the same gap: they only run when someone remembers to
invoke them.

`secret-guard` closes that gap. It doesn't ask to be invoked and it
doesn't audit after the damage is done — it sits on the `PreToolUse`
event for every `Bash` call, for the entire life of the project, and
makes the mistake structurally impossible to commit in the first place.
Where the skill helps you build correctly and the subagent tells you
whether you did, this hook is the automated backstop that actually
stops a secret or a real `.env` from reaching `git commit` at all.

## Status

Demonstrated against the job-pack repo: a `git add` on a file
containing a planted fake Anthropic API key was blocked (exit 2,
nothing staged), and a clean `git add` on an unrelated change passed
through untouched (exit 0). See
[`demo/transcript.md`](demo/transcript.md) for the full run.

## AI use disclosure

Built with Claude Sonnet 5 (Claude Code) per the course AI use policy.
