# vernacular-auditor

A Claude Code subagent for the Job Pack sprint (CS 3660, Sprint 1).

## What it is

`vernacular-auditor` is a **subagent** — a definition file
(`vernacular-auditor.md`) with YAML frontmatter (`name`, `description`,
`tools`, `model`) followed by a system prompt body, matching Claude
Code's subagent format. It is not a skill: a skill (like this project's
[`swap-llm-backend`](../01-skill/SKILL.md)) loads its body inline into
the *current* agentic loop's context when invoked. A subagent is
dispatched via the Task/Agent tool, which spawns a **new, isolated
context** — its own conversation, its own tool budget, working from only
the prompt it's handed — that runs to completion and returns a single
result back to the main loop. It is also not a "child process" in the
OS sense; there's no separate system process, just an isolated LLM
context that the harness manages and reports back through.

That isolation is the point here. The main agentic loop doing
implementation work (adding a backend, wiring persistence, writing the
README) has every reason to be generous with itself about whether a
pattern "counts" — it wrote the code and remembers the intent. The
vernacular-auditor gets none of that context. It only sees what's
actually on disk, which is exactly what the course's LLM grader will
also see.

## Why it exists

Job Pack's Perfect Framework checklist claims several concerns at once:
Strategy (swappable LLM backend), Builder (staged document assembly),
Pipes-and-Filters (the generation pipeline), Persistence (saved
drafts), and Secrets management (API keys). Every one of these can be
*claimed* in the README while only partially existing in the code —
not from dishonesty, just from the ordinary way implementations drift
from their docs over a sprint: a second backend gets stubbed but the
factory never gets updated, a "pipeline" collapses into one function
under deadline pressure, a hardcoded key sneaks in during a debugging
session and never gets pulled back out.

The course's LLM grader checks the code, not the doc's prose. A claim
that reads well but doesn't survive an independent grep costs rubric
points. Running this subagent before every submission is a pre-flight
check against exactly that failure mode.

## How it audits

For each pattern/concern claimed in `README.md` / `ARCHITECTURE.md`,
the subagent independently greps for the pattern's *structural*
signature rather than trusting names or comments:

- **Strategy** — interface + 2 or more implementations + a single
  factory/registry, *and* a leakage check: does any file outside the
  factory import a concrete backend directly, which would break the
  config-only-swap requirement?
- **Builder** — staged mutator calls culminating in one assembly step
  that returns a composite object, not just a multi-argument
  constructor with a `Builder`-shaped name.
- **Pipes-and-Filters** — independently callable/testable transform
  steps chained by an orchestrator, not one function doing several
  things internally.
- **Persistence** — a real ORM model *and* an exercised Create/Read
  path, not a schema class that nothing ever calls.
- **Secrets management** — credentials loaded only from environment
  variables, with zero hardcoded key/token/password literals anywhere
  in tracked source.

Every claim is scored **VERIFIED / WEAK / NOT FOUND** with `file:line`
evidence for what was actually found (or not), plus an overall
**PASS / CONDITIONAL / FAIL** preflight verdict. Full scoring criteria
and the exact grep strategy per pattern are in
[`vernacular-auditor.md`](vernacular-auditor.md).

The subagent is deliberately **read-only**: `tools: Read, Grep, Glob`,
no `Edit`/`Write`/`Bash`. It reports; it does not fix. Acting on a WEAK
or NOT FOUND finding is a separate, explicit step for the main loop (or
a human) to take afterward.

## When to dispatch it

Dispatch `vernacular-auditor` via the Task/Agent tool — not by typing a
slash command, since it's a subagent, not a skill — whenever:

- Before any sprint submission or demo, to pre-flight what the LLM
  grader will check.
- After touching `llm_backends/`, `config.py`, the generation pipeline,
  or persistence code, to confirm the claims in the docs still hold.
- Before opening a PR that changes how a Perfect Framework concern is
  implemented, so the review discussion works from verified structure
  instead of the PR description's prose.

It should run **in addition to**, not instead of, `swap-llm-backend`:
that skill helps *build* a compliant Strategy swap inline while you're
adding a backend; this subagent independently *audits* whatever ended
up on disk, in its own context, with no memory of how it got there.

## What output to expect

A markdown report: one table row per claim (claim text, cited location,
verdict, file:line evidence, notes), followed by an overall verdict
line. A `FAIL` lists exactly which claims are NOT FOUND — the ones
that will cost points if submitted as-is. A `CONDITIONAL` lists which
claims are WEAK and the minimum fix for each. Nothing in the repo is
modified; the report is the entire deliverable, meant to be read by you
(or pasted into a PR/demo-prep note) before deciding what, if anything,
to fix.

## Status

Demonstrated against the job-pack repo (github.com/Hishamelbaw/job-pack)
with an overall **PASS** verdict — all five claims independently
verified, including the Strategy leakage check. See
[`demo/transcript.md`](demo/transcript.md) for the full dispatch and
report.

## AI use disclosure

Built with Claude Sonnet 5 (Claude Code) per the course AI use policy.
