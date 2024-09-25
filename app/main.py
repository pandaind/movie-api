from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.api.v1 import movies
from app.core.exceptions import *


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("Application startup...")
    yield  # Control passes to the app during this time
    # Shutdown event
    logger.info("Application shutdown...")

app = FastAPI(
    title="Movie Database API",
    description="An API for managing a simple movie database. Supports CRUD operations with error handling.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers from the API
app.include_router(movies.router, prefix="/v1/movies", tags=["Movies [v1]"])

# Register global exception handlers
app.add_exception_handler(MovieNotFoundException, movie_not_found_handler)
app.add_exception_handler(MovieAlreadyExistsException, movie_already_exists_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)