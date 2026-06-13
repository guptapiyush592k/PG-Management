from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    detail: str
    error_code: str


class AppException(Exception):
    def __init__(
        self,
        detail: str,
        *,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        error_code: str = "app_error",
    ) -> None:
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(detail)


class NotFoundError(AppException):
    def __init__(self, detail: str = "Resource not found") -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="not_found",
        )


class UnauthorizedError(AppException):
    def __init__(self, detail: str = "Not authenticated") -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="unauthorized",
        )


class ForbiddenError(AppException):
    def __init__(self, detail: str = "Forbidden") -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="forbidden",
        )


class ConflictError(AppException):
    def __init__(self, detail: str = "Resource conflict") -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_409_CONFLICT,
            error_code="conflict",
        )


class ValidationError(AppException):
    def __init__(self, detail: str = "Validation failed") -> None:
        super().__init__(
            detail=detail,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="validation_error",
        )


def _error_payload(detail: str, error_code: str) -> dict[str, Any]:
    return ErrorResponse(detail=detail, error_code=error_code).model_dump()


async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=_error_payload(exc.detail, exc.error_code),
    )


async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=_error_payload("Request validation failed", "request_validation_error"),
    )


async def unhandled_exception_handler(_request: Request, exc: Exception) -> JSONResponse:
    import logging

    logging.getLogger(__name__).exception("Unhandled exception: %s", exc)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=_error_payload("Internal server error", "internal_server_error"),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
