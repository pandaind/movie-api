import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError

from app.api.v1 import movies, users
from app.core.exceptions import (
    MovieNotFoundException,
    MovieAlreadyExistsException,
    movie_not_found_handler,
    movie_already_exists_handler,
    validation_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
)
from app.db.database import init_db
from app.jobs.scheduler_jobs import scheduler
from app.security import api as security

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("Application startup...")
    scheduler.start()
    await init_db()  # Initialize the database and create tables
    yield  # Control passes to the app during this time
    # Shutdown event
    logger.info("Application shutdown...")
    scheduler.shutdown()


app = FastAPI(
    title="Movie Database API",
    description="An API for managing a simple movie database. Supports CRUD operations with error handling.",
    version="1.0.0",
    lifespan=lifespan,
)

# Include routers from the API
app.include_router(movies.router, prefix="/v1/movies", tags=["Movies [v1]"])
app.include_router(users.router, prefix="/v1/users", tags=["Users [v1]"])
app.include_router(security.router, prefix="/v1/security", tags=["Security [v1]"])

# Register global exception handlers
app.add_exception_handler(MovieNotFoundException, movie_not_found_handler)
app.add_exception_handler(MovieAlreadyExistsException, movie_already_exists_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

