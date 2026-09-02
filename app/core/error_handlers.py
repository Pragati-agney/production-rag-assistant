from fastapi import Request
from fastapi.responses import JSONResponse
from app.core.errors import DatabaseError

from app.core.errors import ProviderError

 
async def provider_error_handler(
    request: Request,
    exc: ProviderError,
):
    status_code = 503 if exc.retryable else 500

    if exc.retryable:
        message = (
            "The AI service is temporarily unavailable. "
            "Please try again."
        )
    else:
        message = (
            "The AI service could not process the request."
        )

    return JSONResponse(
        status_code=status_code,
        content={
            "detail": message,
        },
    )

async def database_error_handler(
    request: Request,
    exc: DatabaseError,
):
    return JSONResponse(
        status_code=503,
        content={
            "detail": (
                "The knowledge service is temporarily unavailable. "
                "Please try again."
            )
        },
    )