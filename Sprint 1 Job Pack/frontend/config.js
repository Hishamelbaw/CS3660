// Backend API base URL, no trailing slash.
//
// Local dev (against `uvicorn app.main:app --port 8000`):
//   window.API_BASE_URL = "http://127.0.0.1:8000";
//
// Production: set this to the deployed Render backend's URL, e.g.
//   window.API_BASE_URL = "https://job-pack-api.onrender.com";
window.API_BASE_URL = "http://127.0.0.1:8000";
