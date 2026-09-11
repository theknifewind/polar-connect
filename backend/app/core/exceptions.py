"""Global uniform error handlers — plain-language responses."""

from fastapi import Request
from fastapi.responses import JSONResponse


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler so the client always gets structured JSON."""
    return JSONResponse(
        status_code=500,
        content={
            "error": "Something went wrong on our end. Please try again.",
            "detail": str(exc),
        },
    )


async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    """Turn ValueError into a 400 with a helpful message."""
    return JSONResponse(
        status_code=400,
        content={
            "error": "Invalid input.",
            "detail": str(exc),
        },
    )
