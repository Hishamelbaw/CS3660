from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routes.drafts import router as drafts_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="Job Pack", lifespan=lifespan)

app.include_router(drafts_router)


@app.get("/")
def read_root() -> dict:
    return {"status": "ok", "app": "Job Pack"}
