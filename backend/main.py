"""
main.py — TMA Crew Validator FastAPI application entry point.

Responsibilities:
  - Load environment variables.
  - Configure CORS middleware.
  - Include all four API routers under /api prefix.
  - Expose GET /health.
  - Log startup message.

Run locally:
    cd backend
    uvicorn main:app --reload --port 8000
"""

import logging
import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Load .env before importing routers (routers import GitHubService which reads env)
load_dotenv()

from routers import files, reports, validation, vendors  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------

CORS_ORIGINS: list[str] = [
    o.strip()
    for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    if o.strip()
]

# ---------------------------------------------------------------------------
# Application lifecycle
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("TMA Validator API started")
    logger.info("CORS origins: %s", CORS_ORIGINS)
    yield
    logger.info("TMA Validator API shutting down")


# ---------------------------------------------------------------------------
# FastAPI instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="TMA Crew Validator API",
    description=(
        "REST API for the Trans Maldivian Airways crew scheduling validation system. "
        "Exposes validation pipelines, report retrieval, file management, "
        "and solver vendor configuration."
    ),
    version="2.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(validation.router, prefix="/api")
app.include_router(reports.router,    prefix="/api")
app.include_router(files.router,      prefix="/api")
app.include_router(vendors.router,    prefix="/api")

# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/health", tags=["meta"], summary="Service health check")
def health_check():
    """Return service status and version.  Used by load-balancers and CI."""
    return {"status": "ok", "version": "2.0"}
