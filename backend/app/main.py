"""FastAPI entry point — CORS, routers mount, cookie middleware, lifespan."""

from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.core.exceptions import generic_exception_handler, value_error_handler
from app.routers import assistant, auth, learning, media, repository, stations, stats, studio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create dirs, init DB, run seeds, index pending docs."""
    logger.info("Starting Polar Connect backend …")

    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMADB_DIR, exist_ok=True)

    # Import here to avoid circular imports at module level
    from seeds.seed_runner import run_seeds
    run_seeds()

    logger.info("✓ Polar Connect backend ready")
    yield
    logger.info("Shutting down Polar Connect backend …")


app = FastAPI(
    title="Polar Connect API",
    description=(
        "Backend API for Polar Connect — India's AI-powered "
        "polar science knowledge & outreach platform."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Exception handlers ──────────────────────────────────────
app.add_exception_handler(ValueError, value_error_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, generic_exception_handler)  # type: ignore[arg-type]

# ── Routers ──────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(repository.router)
app.include_router(assistant.router)
app.include_router(learning.router)
app.include_router(stations.router)
app.include_router(media.router)
app.include_router(studio.router)
app.include_router(stats.router)

# ── Static file serving for uploads ─────────────────────────
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# ── Health check ─────────────────────────────────────────────
@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "polar-connect-api"}
