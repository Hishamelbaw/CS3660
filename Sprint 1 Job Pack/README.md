# Job Pack

A single-user app that takes a pasted job description and a candidate profile
and generates a tailored résumé (PDF), cover letter (PDF), and a company-fit
infographic (SVG) via an LLM.

Built for CS 3660 Sprint 1. See [ARCHITECTURE.md](ARCHITECTURE.md) for the
original design plan and [DEPLOY.md](DEPLOY.md) for deployment instructions.

## Stack

- **Backend**: FastAPI (pure JSON API — `app/`)
- **Frontend**: plain HTML/CSS/JS, no build step (`frontend/`)
- **Persistence**: SQLite via SQLAlchemy
- **PDF generation**: `reportlab`
- **Infographic**: hand-built SVG (string templating, no charting library)
- **Deploy target**: backend on Render, frontend on Netlify (see [DEPLOY.md](DEPLOY.md))

The backend and frontend are separate deployable units that talk to each
other over HTTP/CORS — not a single embedded process. See DEPLOY.md for why
and how they're wired together.

## Setup

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows; use `source .venv/bin/activate` on macOS/Linux
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env` and fill in the credentials for whichever `LLM_BACKEND` you're
using (see below). Everything else in `.env.example` has a working default
for local development.

## Running locally

The backend and frontend are two separate static/dynamic servers. Run both:

```bash
# Terminal 1 — backend (reads .env)
uvicorn app.main:app --reload --port 8000

# Terminal 2 — frontend (plain static file server, no build step)
python -m http.server 5500 --directory frontend
```

Open `frontend/config.js` and confirm `window.API_BASE_URL` points at the
backend (`http://127.0.0.1:8000` for the setup above). Then visit
`http://127.0.0.1:5500`.

Because the two servers are on different ports, this is a genuine
cross-origin setup — the backend's `CORS_ALLOWED_ORIGINS` env var must
include `http://127.0.0.1:5500` for the frontend to be able to call it. See
`.env.example`.

## Which LLM backend

`LLM_BACKEND` in `.env` selects the active backend — `hosted_ollama`,
`claude_api`, or `local_ollama`. Whichever this repo is deployed with, it's
recorded in the deployed backend's environment variables (Render dashboard),
not hardcoded anywhere in the code. Check `LLM_BACKEND` there (or in your
local `.env`) to see which one is currently active.

### Swapping backends

Swapping is a config-only change — no code edits, no redeploy of application
logic:

1. Set `LLM_BACKEND` to `hosted_ollama`, `claude_api`, or `local_ollama`.
2. Fill in that backend's credentials in the same `.env` (see the comments
   in `.env.example` for which variables each one needs).
3. Restart the backend process.

This works because every call site goes through `app/config.py`'s
`get_llm_backend()` — no other file imports a concrete backend class
directly (see **Strategy** below).

## Running tests

```bash
python -m pytest tests/ -v
```

12 tests, all offline — no test ever calls a real LLM API (see
`tests/test_pipeline.py`'s `StubBackend` and `tests/test_backends.py`'s
credential fixtures, which only *construct* backends, never call
`.generate()`).

## Design patterns — presentation notes

Five required concerns, and exactly where each one lives:

### 1. Strategy — swappable LLM backends

- `app/llm_backends/base.py` — `LLMBackend` abstract base class, one method:
  `generate(prompt) -> str`.
- `app/llm_backends/hosted_ollama.py`, `claude_api.py`, `local_ollama.py` —
  three interchangeable implementations.
- `app/config.py` — `get_llm_backend()` is the **only** factory/registry.
  It reads `LLM_BACKEND` from the environment and returns the matching
  instance. No other module imports a concrete backend class — that's what
  makes swapping a config-only change (`tests/test_backends.py` proves this:
  parametrized over all three backend names, plus the default and the
  invalid-value rejection).

### 2. Builder — staged construction of the JobPack

- `app/builders/job_pack_builder.py` — `JobPackBuilder` assembles a `JobPack`
  (résumé PDF + cover letter PDF + infographic SVG) step by step
  (`build_resume()` → `build_cover_letter()` → `build_infographic()` →
  `build()`) from a shared context dict (the pipeline's output). This is a
  different pattern from Strategy on purpose — it's staged construction of a
  composite output, not swappable behavior.
- `app/artifacts/` — the actual renderers each build step delegates to
  (`resume_pdf.py`, `cover_letter_pdf.py`, `infographic_svg.py`, plus a
  shared `_pdf_utils.py` helper for pagination/wrapping).

### 3. Pipes-and-Filters (EIP) — the generation pipeline

- `app/pipeline/base.py` — `Filter` interface (`process(context) -> context`)
  and a `Pipeline` runner that chains them.
- `app/pipeline/filters.py` — the four filters: `ParseInputsFilter` →
  `BuildPromptsFilter` → `CallLLMFilter` (this is where the Strategy backend
  gets invoked) → `PostProcessFilter`. The pipeline's output context is
  exactly what `JobPackBuilder` consumes — that's the seam between the two
  patterns.

### 4. Persistence

- `app/models.py` — `Draft` ORM model (job description, candidate profile,
  which backend generated it, the three artifact texts, title, timestamp).
- `app/db.py` — SQLAlchemy engine/session setup, reads `DATABASE_URL` from
  the environment.
- `app/routes/drafts.py` — `POST/GET /api/drafts`, `GET/DELETE
  /api/drafts/{id}`. The frontend's compare view is two of these `GET`
  calls side by side (`frontend/app.js`'s `handleCompare()`).

### 5. Secrets management

- All credentials (`ANTHROPIC_API_KEY`, `CLASS_OLLAMA_API_KEY`, etc.) are
  read from the environment via `os.environ`, never hardcoded — see any
  `llm_backends/*.py` file.
- `.env` is gitignored; `.env.example` ships placeholders only.
- Same discipline extends to `CORS_ALLOWED_ORIGINS` (which origins may call
  the API) and `DATABASE_URL` — nothing environment-specific lives in code.

## Project structure

```
Sprint 1 Job Pack/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── DEPLOY.md
├── render.yaml              # Render Blueprint (backend)
├── netlify.toml             # Netlify config (frontend)
├── app/
│   ├── main.py               # FastAPI app, CORS, router wiring
│   ├── config.py              # Strategy factory: get_llm_backend()
│   ├── db.py                  # SQLAlchemy engine/session
│   ├── models.py               # Draft ORM model
│   ├── schemas.py              # Pydantic request/response models
│   ├── llm_backends/           # Strategy: base.py + 3 implementations
│   ├── pipeline/                # Pipes-and-Filters: base.py + filters.py
│   ├── builders/                 # Builder: job_pack_builder.py
│   ├── artifacts/                 # PDF/SVG renderers used by the builder
│   └── routes/                     # generate.py, drafts.py
├── frontend/                # static bundle (Netlify): index.html, app.js, style.css, config.js
└── tests/                   # test_pipeline.py, test_builder.py, test_backends.py
```
