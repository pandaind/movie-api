import logging
from contextlib import asynccontextmanager

import joblib
import requests
from fastapi import Body, FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from huggingface_hub import hf_hub_url
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.api.profiler import ProfileEndpointsMiddleWare
from app.api.rate_limit import limiter
from app.api.v1 import movies, users
from app.chat import chat_room, secure_chat_room, ws_security
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
from app.gql.gql_utils import graphql_app
from app.grpc import api as grpc
from app.jobs.scheduler_jobs import scheduler
from app.middleware.asgi_middleware import ASGIMiddleware, asgi_middleware
from app.middleware.middleware import ClientInfoMiddleware
from app.middleware.req_middleware import HashBodyContentMiddleWare
from app.middleware.res_middleware import ExtraHeadersResponseMiddleware
from app.middleware.webhook import Event, WebhookSenderMiddleWare
from app.ml import doctor
from app.ml.doctor import FILENAME, REPO_ID, ml_model
from app.security import api as security
from app.security import github_login, mfa

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup event
    logger.info("Application startup...")
    scheduler.start()
    await init_db()  # Initialize the database and create tables

    # Download the file with SSL verification disabled
    url = hf_hub_url(repo_id=REPO_ID, filename=FILENAME)
    response = requests.get(url, verify=False)
    with open(FILENAME, "wb") as f:
        f.write(response.content)

    # Load the model
    ml_model["doctor"] = joblib.load(FILENAME)

    yield  # Control passes to the app during this time
    ml_model.clear()
    # Shutdown event
    logger.info("Application shutdown...")
    scheduler.shutdown()


app = FastAPI(
    title="Movie Database API",
    description="An API for managing a simple movie database. Supports CRUD operations with error handling.",
    version="1.0.0",
    lifespan=lifespan,
    middleware=[
        Middleware(
            ASGIMiddleware,
            parameter="example_parameter",
        ),
        Middleware(
            asgi_middleware,
            parameter="example_parameter",
        ),
    ],
)

app.add_middleware(
    HashBodyContentMiddleWare,
    allowed_paths=["/v1/doctor/send"],
)

app.add_middleware(
    ExtraHeadersResponseMiddleware,
    headers=(
        ("new-header", "fastapi-demo"),
        ("another-header", "another"),
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"],
)

# app.add_middleware(
#     WebhookSenderMiddleWare,
# )

# Configure RateLimit
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

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
app.include_router(
    secure_chat_room.router, prefix="/v1/secure-chat", tags=["Secure Chatroom [v1]"]
)
app.include_router(ws_security.router, prefix="/v1/wss", tags=["WS Security [v1]"])
app.include_router(grpc.router, prefix="/v1/grpc", tags=["gRPC [v1]"])
app.include_router(graphql_app, prefix="/graphql")
app.include_router(doctor.router, prefix="/v1/doctor", tags=["Doctor [v1]"])

# Register global exception handlers
app.add_exception_handler(MovieNotFoundException, movie_not_found_handler)
app.add_exception_handler(MovieAlreadyExistsException, movie_already_exists_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)


# @app.get("/get")
# async def send():
#     return {"message": "Hello World"}
#
#
# @app.post("/register-webhook-url")
# async def add_webhook_url(request: Request, url: str = Body()):
#     if not url.startswith("http"):
#         url = f"http://{url}"
#     request.state.webhook_urls.add(url)
#     return {"url added": url}
#
#
# @app.webhooks.post("/fastapi-webhook")
# def fastapi_webhook(event: Event):
#     """_summary_
#
#     Args:
#         event (Event): Received event from webhook
#         It contains information about the
#         host, path, timestamp and body of the request
#     """
