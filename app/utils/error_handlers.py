import logging
from typing import Any

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse

from app.models.schemas import ErrorResponse

logger = logging.getLogger(__name__)


def register_error_handlers(app: FastAPI) -> None:
    """Registra manejadores de errores globales para la aplicación FastAPI."""

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        logger.warning("Excepción HTTP %s en %s", exc.status_code, request.url.path)

        detail: Any
        if isinstance(exc.detail, dict):
            detail = exc.detail
        else:
            detail = ErrorResponse(
                error=str(exc.detail),
                code=exc.status_code,
            ).model_dump()

        return JSONResponse(status_code=exc.status_code, content=detail)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.error("Excepción no manejada en %s: %s", request.url.path, exc, exc_info=True)

        error = ErrorResponse(
            error="Error interno del servidor",
            code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            details=str(exc),
        )
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=error.model_dump())
