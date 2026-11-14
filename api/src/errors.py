"""API error classes, the error payload builder and FastAPI exception handlers."""

import logging
from typing import Any

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from constants import SCHEMA_MODEL_DUMP_JSON_MODE
from schemas import ErrorBody, ErrorDetail, ErrorResponse

logger = logging.getLogger(__name__)


class ApiError(Exception):
    """Base class for expected API errors."""

    status_code = 500
    code = "INTERNAL_ERROR"

    def __init__(self, message: str, details: list[dict[str, Any]] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details


class ValidationApiError(ApiError):
    """400: invalid input (bad number, unknown filter slug, min > max...)."""

    status_code = 400
    code = "VALIDATION_ERROR"


class NotFoundError(ApiError):
    """404: unknown or hidden resource (R1, R4)."""

    status_code = 404
    code = "NOT_FOUND"


def error_payload(
    code: str, message: str, details: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Build the shared `{"error": {...}}` JSON payload."""
    body = ErrorBody(
        code=code,
        message=message,
        details=[ErrorDetail(**d) for d in details] if details else None,
    )
    return ErrorResponse(error=body).model_dump(
        mode=SCHEMA_MODEL_DUMP_JSON_MODE, exclude_none=True
    )


def _json(status: int, code: str, message: str, details=None) -> JSONResponse:
    return JSONResponse(
        status_code=status, content=error_payload(code, message, details)
    )


def handle_exception(error: Exception) -> JSONResponse:
    """
    Convert any exception raised in a router into the shared error response.

    Args:
        error (Exception): The exception caught in the router.

    Returns:
        JSONResponse: Error response (`ApiError` keeps its status, anything else is a 500).
    """
    if isinstance(error, ApiError):
        return _json(error.status_code, error.code, error.message, error.details)
    logger.exception("Unhandled error", exc_info=error)
    return _json(500, "INTERNAL_ERROR", "Unexpected server error")


def register_exception_handlers(app: FastAPI) -> None:
    """Attach handlers so every error uses the shared shape."""

    @app.exception_handler(ApiError)
    async def api_error(_: Request, exc: ApiError):
        return _json(exc.status_code, exc.code, exc.message, exc.details)

    @app.exception_handler(RequestValidationError)
    async def validation_error(_: Request, exc: RequestValidationError):
        details = [
            {
                "field": str(e["loc"][-1]) if e.get("loc") else None,
                "value": (
                    e.get("input")
                    if isinstance(e.get("input"), (str, int, float, bool))
                    else None
                ),
                "message": e.get("msg"),
            }
            for e in exc.errors()
        ]
        first = details[0] if details else {}
        message = (
            f"{first.get('field')}: {first.get('message')}"
            if first
            else "Invalid input"
        )
        return _json(400, "VALIDATION_ERROR", message, details)

    @app.exception_handler(StarletteHTTPException)
    async def http_error(_: Request, exc: StarletteHTTPException):
        code = "NOT_FOUND" if exc.status_code == 404 else "HTTP_ERROR"
        return _json(exc.status_code, code, str(exc.detail))

    @app.exception_handler(Exception)
    async def unexpected_error(_: Request, exc: Exception):
        logger.exception("Unhandled error")
        return _json(500, "INTERNAL_ERROR", "Unexpected server error")
