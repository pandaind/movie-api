import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pyinstrument import Profiler
from pyinstrument.renderers import SpeedscopeRenderer
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

profiler = Profiler(
    interval=0.0001, async_mode="enabled"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    profiler.start()
    yield
    profiler.stop()
    profiler.write_html(os.getcwd() + "/profiler.html")


class ProfileEndpointsMiddleWare(BaseHTTPMiddleware):
    async def dispatch(
            self, request: Request, call_next
    ):
        if not profiler.is_running:
            profiler.start()
        response = await call_next(request)
        if profiler.is_running:
            profiler.stop()
            with open(
                    os.getcwd() + "/profiler2.json", "w"
            ) as file:
                file.write(
                    profiler.output(
                        SpeedscopeRenderer()
                    )
                )
            profiler.write_html(
                os.getcwd() + "/profiler.html"
            )
            profiler.start()
        return response