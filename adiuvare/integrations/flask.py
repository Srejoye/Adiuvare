import asyncio
import json

from werkzeug.wrappers import Request, Response

from ..core.models import RequestContext


class AdiuvareMiddleware:
    def __init__(self, app, guard) -> None:
        self._app = app
        self._guard = guard

    def __call__(self, environ, start_response):
        req = Request(environ)
        body = req.get_data(cache=True, as_text=True)
        ctx = RequestContext(
            identity=req.headers.get("x-user-id", req.remote_addr or "anon"),
            payload=body or None,
            url=req.path,
            method=req.method,
            headers=dict(req.headers),
            ip=req.remote_addr or "127.0.0.1",
            endpoint=req.path,
            snapshot=self._guard._cfg_snap,
        )

        gate, event = asyncio.run(self._guard.inspect(ctx))
        if not gate.passed:
            res = Response(
                json.dumps({"detail": gate.block_reason or "blocked"}),
                status=gate.status_code,
                content_type="application/json",
            )
            return res(environ, start_response)

        environ["adiuvare.event"] = event
        return self._app(environ, start_response)
