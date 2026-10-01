"""FastAPI application entrypoint for the Interview Service."""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.api.routes import interviews, questions, system
from app.core.config import get_settings
from app.core.exceptions import AppError
from app.infrastructure.database.mongodb import MongoDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    mongodb = MongoDB(settings)
    await mongodb.connect()
    app.state.mongodb = mongodb
    logger.info("Interview Service started (env=%s)", settings.APP_ENV)
    try:
        yield
    finally:
        await mongodb.disconnect()
        logger.info("Interview Service shut down")


app = FastAPI(
    title="Interview Service",
    description="Manages interview sessions, question pools, and feedback for Interview Assistant.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    """Centralized mapping of domain/application errors to HTTP responses.

    Never leaks internals (stack traces, Mongo details) to clients.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.error_code,
            "message": exc.message,
            "details": exc.extra or None,
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"error_code": "internal_error", "message": "An unexpected error occurred"},
    )


# System endpoints (health/ready/dev-token) are mounted at the root, not under the API prefix.
app.include_router(system.router)

app.include_router(interviews.router, prefix=settings.API_V1_PREFIX)
app.include_router(questions.router, prefix=settings.API_V1_PREFIX)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8080, reload=settings.APP_ENV == "development")
