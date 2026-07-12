"""
Personalized Networking Assistant - FastAPI Application Entrypoint
======================================================================

Run locally with:

    uvicorn app.main:app --reload

Interactive API docs are then available at http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.routers import conversation

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Personalized Networking Assistant API",
    description=(
        "AI-powered API that extracts event themes, generates personalized "
        "networking conversation starters, and fact-checks topics via Wikipedia."
    ),
    version="1.0.0",
)

# Allow the static frontend (opened via file:// or served from any local
# port) to call the API during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Return a clean 422 payload instead of FastAPI's default verbose trace."""
    logger.warning("Validation error on %s: %s", request.url.path, exc.errors())
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "message": "Invalid request payload."},
    )


@app.get("/", tags=["Health"])
def root() -> dict:
    """Basic health check / welcome route."""
    return {
        "message": "Personalized Networking Assistant API is running.",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health() -> dict:
    return {"status": "ok"}


app.include_router(conversation.router, tags=["Conversation"])
