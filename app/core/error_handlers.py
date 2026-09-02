from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.errors import DatabaseError, ProviderError


async def provider_error_handler(
    request: Request,
    exc: Exception,
):
    if not isinstance(exc, ProviderError):
        raise exc

    return JSONResponse(
        status_code=503 if exc.retryable else 500,
        content={
            "detail": (
                "The AI service is temporarily unavailable. Please try again."
            )
        },
    )


async def database_error_handler(
    request: Request,
    exc: Exception,
):
    if not isinstance(exc, DatabaseError):
        raise exc

    return JSONResponse(
        status_code=503 if exc.retryable else 500,
        content={
            "detail": (
                "The knowledge service is temporarily unavailable. Please try again."
            )
        },
    )
