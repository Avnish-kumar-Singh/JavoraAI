"""
JavaMentorAI HTTP API.

Run with:
    uvicorn app.api.server:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.db import init_db
from app.api.routes import auth, chat, history
from app.config.logging_config import logger
from app.config.settings import settings

FRONTEND_DIR = Path(__file__).resolve().parents[2] / "frontend"


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    logger.info("Database ready.")

    # Pre-load the model and compile the graph so the first user request
    # doesn't pay for either.
    try:
        from app.core.container import get_graph, get_llm_service

        get_graph()
        get_llm_service().warmup()
    except Exception:
        logger.warning("Startup warmup skipped.")

    yield


app = FastAPI(
    title="JavaMentorAI API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(history.router)


@app.get("/api/health")
def health():
    return {"status": "ok", "model": settings.MODEL_NAME}


# Serve the UI from the same origin so there are no CORS surprises.
if FRONTEND_DIR.exists():
    app.mount(
        "/static",
        StaticFiles(directory=str(FRONTEND_DIR)),
        name="static",
    )

    @app.get("/")
    def index():
        return FileResponse(str(FRONTEND_DIR / "index.html"))
