import logging
import os
from contextlib import asynccontextmanager
from sys import prefix

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.profiler import ProfileEndpointsMiddleWare
from app.api.rate_limit import limiter
from app.api.v1 import movies, users
from app.core.config import settings
from app.core.exceptions import (
    MovieAlreadyExistsException,
    MovieNotFoundException,
    http_exception_handler,
    movie_already_exists_handler,
    movie_not_found_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)
from app.db.database import init_db
from app.jobs.scheduler_jobs import scheduler
from app.middleware.middleware import ClientInfoMiddleware
from app.security import api as security
from app.security import github_login, mfa
from app.chat import chat_room, secure_chat_room, ws_security

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

# Configure RateLimit
app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded, _rate_limit_exceeded_handler
)

# Add middleware to log client information
app.add_middleware(ClientInfoMiddleware)

# Add middleware to profile endpoint
if settings.enable_profiling:
    app.add_middleware(ProfileEndpointsMiddleWare)

# Include routers from the API
app.include_router(movies.router, prefix="/v1/movies", tags=["Movies [v1]"])
app.include_router(users.router, prefix="/v1/users", tags=["Users [v1]"])
app.include_router(security.router, prefix="/v1/security", tags=["Security [v1]"])
app.include_router(github_login.router, prefix="/v1/github", tags=["Github [v1]"])
app.include_router(mfa.router, prefix="/v1/mfa", tags=["MFA [v1]"])
app.include_router(chat_room.router, prefix="/v1/chat", tags=["Chatroom [v1]"])
app.include_router(secure_chat_room.router, prefix="/v1/secure-chat", tags=["Secure Chatroom [v1]"])
app.include_router(ws_security.router, prefix="/v1/wss", tags=["WS Security [v1]"])

# Register global exception handlers
app.add_exception_handler(MovieNotFoundException, movie_not_found_handler)
app.add_exception_handler(MovieAlreadyExistsException, movie_already_exists_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)
