from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from starlette.types import ASGIApp

from ..core.models import RequestContext


class AdiuvareMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, guard) -> None:
        super().__init__(app)
        self._guard = guard

    async def dispatch(self, request: Request, call_next):
        body = await request.body()
        ctx = RequestContext(
            identity=request.headers.get("x-user-id", request.client.host if request.client else "anon"),
            payload=body.decode() if body else None,
            url=str(request.url.path),
            method=request.method,
            headers=dict(request.headers),
            ip=request.client.host if request.client else "127.0.0.1",
            endpoint=request.url.path,
        )

        gate, event = await self._guard.inspect(ctx)
        if not gate.passed:
            return JSONResponse(
                {"detail": gate.block_reason or "blocked"},
                status_code=gate.status_code,
            )

        request.state.adiuvare_event = event
        return await call_next(request)
