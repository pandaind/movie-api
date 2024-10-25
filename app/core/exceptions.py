from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.logger import logger


class MovieNotFoundException(Exception):
    def __init__(self, movie_id: int):
        self.movie_id = movie_id


class MovieAlreadyExistsException(Exception):
    def __init__(self, movie_title: str):
        self.movie_title = movie_title


# Handler for Movie Not Found
async def movie_not_found_handler(request: Request, exc: MovieNotFoundException):
    return JSONResponse(
        status_code=404, content={"detail": f"Movie with ID {exc.movie_id} not found."}
    )


# Handler for Movie Already Exists
async def movie_already_exists_handler(
    request: Request, exc: MovieAlreadyExistsException
):
    return JSONResponse(
        status_code=400,
        content={"detail": f"Movie '{exc.movie_title}' already exists."},
    )


# Custom Exception Handler for HTTPException
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException: {exc.detail} (status: {exc.status_code})")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "error": "HTTPException occurred"},
    )


# Handler for validation errors (Pydantic)
async def validation_exception_handler(request: Request, exc: ValidationError):
    logger.warning(f"Validation Error: {exc.errors()}")
    return JSONResponse(
        status_code=422, content={"detail": exc.errors(), "error": "Validation error"}
    )


# Catch-all for any unhandled exceptions
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.critical(f"Unhandled Exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred", "error": str(exc)},
    )
