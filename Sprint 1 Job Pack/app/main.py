from fastapi import FastAPI

app = FastAPI(title="Job Pack")


@app.get("/")
def read_root() -> dict:
    return {"status": "ok", "app": "Job Pack"}
