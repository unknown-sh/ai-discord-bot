import logging
import traceback
from typing import Callable, Awaitable

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware


class GlobalErrorMiddleware(BaseHTTPMiddleware):
    """
    Middleware to catch and handle all uncaught exceptions globally for FastAPI.
    Returns JSON error responses for validation, HTTP, and internal errors.
    """
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable]) -> JSONResponse:
        try:
            response = await call_next(request)
            return response
        except RequestValidationError as exc:
            logging.warning(
                f"Validation error: {exc.errors()} | Body: {await request.body()}"
            )
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={"detail": exc.errors(), "message": "Validation error."},
            )
        except StarletteHTTPException as exc:
            logging.warning(f"HTTPException: {exc.detail}")
            return JSONResponse(
                status_code=exc.status_code,
                content={"detail": exc.detail, "message": "HTTP error."},
            )
        except Exception as exc:
            tb = traceback.format_exc()
            logging.error(f"Unhandled exception: {exc}\n{tb}")
            return JSONResponse(
                status_code=500,
                content={"detail": str(exc), "message": "Internal server error."},
            )
