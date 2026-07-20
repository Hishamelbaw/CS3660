# Demonstration transcript

A real run of the `vernacular-auditor` subagent against
[job-pack](https://github.com/Hishamelbaw/job-pack) (the Sprint 1 repo
this pattern of subagent was built to pre-flight).

## Dispatch

Invocation, in the main agentic loop working in the job-pack repo:

> Use the vernacular-auditor subagent to audit this repo's README.md
> claims against the actual code.

This dispatches via the Task/Agent tool, spawning `vernacular-auditor`
in its own isolated context — no memory of how the code was written,
only what's on disk:

```
vernacular-auditor(Audit README.md claims against actual code)
  Done (33 tool uses · 25.5k tokens · 1m 34s)
```

## Report (verbatim)

```
Vernacular Audit — job-pack

Overall verdict: PASS

All five architectural claims check out with structural evidence:

| Claim | Verdict | Key Evidence |
|---|---|---|
| Strategy — swappable LLM backends via get_llm_backend() factory | VERIFIED | app/llm_backends/base.py:4-9 (ABC); 3 concrete impls; app/config.py:12-30 (factory). Zero leakage into business logic. |
| Builder — staged JobPackBuilder with mutators + terminal build() | VERIFIED | app/builders/job_pack_builder.py:16-49; three self-returning mutators accumulate partial state; build():38 assembles final JobPack. |
| Pipes-and-Filters — Filter ABC + Pipeline runner + 4 filter classes | VERIFIED | app/pipeline/base.py:5-22; app/pipeline/filters.py has 4 independently-testable filter classes; tests/test_pipeline.py covers isolation and full-chain. |
| Persistence — Draft ORM model, SQLAlchemy session, Create/Read routes | VERIFIED | app/models.py:9-22; app/db.py:5-32; app/routes/drafts.py covers Create, Read (list + single), and Delete. |
| Secrets management — env vars only, no hardcoded literals, .env gitignored | VERIFIED | Every credential via os.environ; regex scan found zero hardcoded key material; .gitignore:2 lists .env; .env.example has placeholders only. |

One minor note: persistence uses Base.metadata.create_all on startup
rather than Alembic migrations — sufficient for SQLite but worth
flagging if the project ever moves to a managed database.
```

## Takeaway

Every claim in job-pack's README survived independent structural
verification — including the Strategy leakage check, which is the
failure mode this subagent exists to catch. The one flagged note
(no migration tooling) isn't a scored claim in the README, so it
didn't affect the verdict, but it's exactly the kind of forward-looking
observation worth carrying into the next sprint.
