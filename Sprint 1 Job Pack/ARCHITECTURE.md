# Job Pack — Architecture Plan (Sprint 1)

Solo build (professor-approved). Target: 2-week single-process Python app.

## Stack

- Backend: FastAPI (single process serves both the API and the static
  frontend — satisfies "embedded" backend requirement).
- Persistence: SQLite via SQLAlchemy.
- Frontend: plain HTML/CSS/JS served from `app/static/` + `app/templates/`
  (no build step, keeps deploy simple).
- PDF generation: `reportlab` (résumé, cover letter).
- Infographic: hand-built SVG (string templating — no extra dependency).
- Deploy target: uvucs.org (whole process deployed there covers both the
  "frontend on uvucs.org" and "backend embedded" requirements in one shot).
  Fallback if uvucs.org access is unavailable: Render or Fly.io free tier.

## Required patterns and where they live

**GoF #1 — Strategy.** `app/llm_backends/base.py` defines `LLMBackend`
(abstract `generate(prompt) -> str`). Three implementations:
`hosted_ollama.py`, `claude_api.py`, `local_ollama.py`. `app/config.py`
holds the only registry/factory (`get_llm_backend()`), reading
`LLM_BACKEND` from the environment. No other file imports a concrete
backend — this is what makes swapping backends a config-only change.

**GoF #2 — Builder.** `app/builders/job_pack_builder.py` — `JobPackBuilder`
assembles a `JobPack` (résumé PDF, cover letter PDF, infographic SVG)
step by step from a shared context object (LLM-generated résumé text,
cover letter text, fit analysis). This is a genuinely different pattern
from Strategy — it's about staged construction of a composite output,
not swappable behavior.

**EIP — Pipes-and-Filters.** `app/pipeline/base.py` defines a `Filter`
interface (`process(context) -> context`) and a `Pipeline` runner that
chains filters. `app/pipeline/filters.py` implements: `ParseInputsFilter`
→ `BuildPromptsFilter` → `CallLLMFilter` (uses the Strategy backend) →
`PostProcessFilter`. The pipeline's output context feeds the
`JobPackBuilder`. This is the LLM pipeline the rubric asks for.

**Perfect Framework concern #1 — Persistence.** `app/models.py` (`Draft`
table: job_description, candidate_profile, backend_used, resume_text,
cover_letter_text, infographic_svg, title, created_at). `app/db.py` sets
up the SQLAlchemy engine/session. `app/routes/drafts.py` exposes
save/list/get/delete so ≥2 drafts for the same job can be saved, reopened,
edited, and compared (a simple side-by-side compare view in the frontend
reading two draft IDs).

**Perfect Framework concern #2 — Secrets management.** All keys
(`CLASS_OLLAMA_API_KEY`, `ANTHROPIC_API_KEY`, etc.) come from `.env` via
`os.environ`, never hardcoded. `.env` is gitignored; `.env.example` ships
placeholders only. (This is the same discipline the `swap-llm-backend`
skill audits — worth reusing that skill here once it's on your machine.)

## File structure

```
job-pack/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── app/
│   ├── main.py                   # FastAPI app; mounts routers + static
│   ├── config.py                 # Strategy factory: get_llm_backend()
│   ├── db.py                     # SQLAlchemy engine/session
│   ├── models.py                 # Draft ORM model
│   ├── schemas.py                # Pydantic request/response models
│   ├── llm_backends/
│   │   ├── base.py               # LLMBackend ABC (Strategy interface)
│   │   ├── hosted_ollama.py
│   │   ├── claude_api.py
│   │   └── local_ollama.py
│   ├── pipeline/
│   │   ├── base.py               # Filter ABC + Pipeline runner
│   │   └── filters.py
│   ├── builders/
│   │   └── job_pack_builder.py
│   ├── artifacts/
│   │   ├── resume_pdf.py
│   │   ├── cover_letter_pdf.py
│   │   └── infographic_svg.py
│   ├── routes/
│   │   ├── generate.py           # POST /api/generate
│   │   └── drafts.py             # CRUD /api/drafts
│   ├── static/                   # JS/CSS
│   └── templates/                # HTML (Jinja2)
└── tests/
    ├── test_pipeline.py
    ├── test_builder.py
    └── test_backends.py
```

## Suggested build order (also the order to hand to Claude Code)

1. Scaffold FastAPI app skeleton + `.env.example` + `.gitignore` (get a
   "hello world" route deployed early — deployability is 10 rubric points
   and easiest to lose by leaving it to the last day).
2. `llm_backends/` + `config.py` — Strategy layer, with `hosted_ollama`
   and `claude_api` as the two required backends. Test swapping via
   `.env` only.
3. `pipeline/` — Pipes-and-Filters, wired to the Strategy backend.
4. `builders/` + `artifacts/` — Builder pattern producing the three
   outputs.
5. `models.py` + `db.py` + `routes/drafts.py` — persistence, save/reopen/
   compare.
6. Frontend — single page: paste job description + profile, generate,
   view/download three artifacts, save/list/compare drafts.
7. Deploy. Confirm HTTPS.
8. Tests for the pipeline, builder, and backend registry (stretch: real
   coverage counts toward the regression-suite bonus).
9. README: setup, which backend you used, how to swap, plus prep the
   presentation notes naming Strategy, Builder, Pipes-and-Filters,
   Persistence, and Secrets Management explicitly.

## First prompt to give Claude Code

> I'm building "Job Pack" for CS 3660 Sprint 1 — a single-user FastAPI
> app that takes a pasted job description + candidate profile and
> generates a tailored résumé PDF, cover letter PDF, and a company-fit
> infographic SVG. Read ARCHITECTURE.md in this repo for the full design
> — it specifies a Strategy pattern for swappable LLM backends
> (hosted_ollama, claude_api), a Builder pattern for assembling the three
> output artifacts, a Pipes-and-Filters pipeline for the generation
> steps, SQLite persistence for drafts, and .env-based secrets
> management. Scaffold the project per the file structure and build
> order in ARCHITECTURE.md, starting with step 1 (FastAPI skeleton,
> .env.example, .gitignore, a working root route). Stop after each step
> so I can review before continuing.
