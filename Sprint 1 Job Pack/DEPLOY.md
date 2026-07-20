# Deploying Job Pack

The app is split into two independently-deployed pieces:

- **Backend** (`app/`) — FastAPI, deployed to **Render** as a web service.
- **Frontend** (`frontend/`) — plain static HTML/CSS/JS, no build step, deployed to **Netlify**.

They run on different origins, so the backend allows the frontend's origin via CORS
(`CORS_ALLOWED_ORIGINS`), and the frontend is told where the backend lives via
`frontend/config.js` (`window.API_BASE_URL`).

Deploy the backend first — you need its URL before the frontend config makes sense.

## 1. Backend on Render

### Option A — Blueprint (`render.yaml`)

1. Push this repo to GitHub/GitLab.
2. In Render: **New +** → **Blueprint**, point it at the repo.
3. If the repo has other projects in it, set **Root Directory** to `Sprint 1 Job Pack`
   (the folder containing `render.yaml`).
4. Render reads `render.yaml` and creates the `job-pack-api` web service. Fill in the
   prompted environment variables (see below) before the first deploy.

### Option B — Manual web service

1. Render: **New +** → **Web Service**, connect the repo.
2. **Root Directory**: `Sprint 1 Job Pack` (if applicable).
3. **Runtime**: Python 3.
4. **Build Command**: `pip install -r requirements.txt`
5. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. Add the environment variables below under the service's **Environment** tab.

### Environment variables

Set whichever backend you're using, per `.env.example`:

| Variable | Notes |
|---|---|
| `LLM_BACKEND` | `hosted_ollama`, `claude_api`, or `local_ollama` |
| `CLASS_OLLAMA_BASE_URL`, `CLASS_OLLAMA_API_KEY`, `CLASS_OLLAMA_MODEL` | only if using `hosted_ollama` |
| `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL` | only if using `claude_api` |
| `LOCAL_OLLAMA_BASE_URL`, `LOCAL_OLLAMA_MODEL` | only if using `local_ollama` (rare in production) |
| `DATABASE_URL` | `sqlite:///./job_pack.db` works, but see the caveat below |
| `CORS_ALLOWED_ORIGINS` | comma-separated origins allowed to call the API — set this to your Netlify site's URL once you have it (step 2) |

**SQLite caveat:** Render's free-tier filesystem is ephemeral — it resets on every
redeploy/restart, so saved drafts won't persist across deploys. That's an acceptable
tradeoff for this sprint (single-user, SQLite-by-design per `ARCHITECTURE.md`); if
persistence across deploys matters later, attach a Render Disk or move to a managed
Postgres instance.

Once deployed, note the service URL, e.g. `https://job-pack-api.onrender.com`.

## 2. Frontend on Netlify

First, edit `frontend/config.js` and set:

```js
window.API_BASE_URL = "https://job-pack-api.onrender.com"; // your Render URL from step 1
```

### Option A — Git-connected (`netlify.toml`)

1. Netlify: **Add new site** → **Import an existing project**, connect the repo.
2. If the repo has other projects in it, set **Base directory** to `Sprint 1 Job Pack`.
3. Netlify reads `netlify.toml`, which sets `publish = "frontend"`. No build command needed.
4. Deploy.

### Option B — Manual drag-and-drop

1. Netlify: **Sites** → drag the `frontend/` folder onto the "Deploys" drop zone.
2. Netlify serves it as-is — no build step, no git connection required.

Once deployed, note the site URL, e.g. `https://job-pack.netlify.app`.

## 3. Close the loop

Go back to the Render service and set `CORS_ALLOWED_ORIGINS` to the Netlify URL from
step 2 (comma-separate multiple origins if needed, e.g. also keeping a local dev
origin). Redeploy/restart the backend so the new value takes effect.

## Local development across origins

To reproduce the two-origin setup locally before deploying:

```bash
# Terminal 1 — backend
CORS_ALLOWED_ORIGINS=http://127.0.0.1:5500 uvicorn app.main:app --port 8000

# Terminal 2 — frontend (plain static file server, no build step)
python -m http.server 5500 --directory frontend
```

Set `frontend/config.js`'s `window.API_BASE_URL` to `http://127.0.0.1:8000`, then open
`http://127.0.0.1:5500`.
