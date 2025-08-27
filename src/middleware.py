import time

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class ProcessTimeMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add process time header to the response.
    """

    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        response.headers["X-Process-Time"] = f"{duration:.3f}s"
        return response
