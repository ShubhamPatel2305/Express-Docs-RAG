"""FastAPI entrypoint.

Kept slim: middleware + routers + a friendly root. Anything heavier belongs in
app/rag or app/ingestion.
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import chat, health
from app.rag.idle_manager import start_idle_monitor, stop_idle_monitor


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_idle_monitor()
    yield
    stop_idle_monitor()


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title=s.app_name, version="1.0.0", lifespan=lifespan)

    origins = [o.strip() for o in s.cors_origins.split(",") if o.strip()]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(chat.router)

    @app.get("/")
    def root() -> dict:
        return {"name": s.app_name, "docs": "/docs"}

    return app


app = create_app()