from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from adiuvare import Guard


def test_fastapi_middleware_allows_clean_request():
    app = FastAPI()
    guard = Guard()
    guard.use(app, framework="fastapi")

    @app.get("/ping")
    async def ping(request: Request):
        assert request.state.adiuvare_event is not None
        return {"ok": True}

    client = TestClient(app)
    res = client.get("/ping", headers={"User-Agent": "Mozilla/5.0", "x-user-id": "u1"})
    assert res.status_code == 200
    assert res.json() == {"ok": True}


def test_fastapi_middleware_blocks_when_identity_is_blocked():
    app = FastAPI()
    guard = Guard()
    guard._id_store.set_blocked("u1", 60)
    guard.use(app, framework="fastapi")

    @app.get("/ping")
    async def ping():
        return {"ok": True}

    client = TestClient(app)
    res = client.get("/ping", headers={"User-Agent": "Mozilla/5.0", "x-user-id": "u1"})
    assert res.status_code == 429


def test_guard_event_hook_sees_pipeline_event():
    app = FastAPI()
    guard = Guard()
    seen = []

    @guard.hooks.on_event
    def _take(event):
        seen.append(event.verdict)

    guard.use(app, framework="fastapi")

    @app.post("/login")
    async def login():
        return {"ok": True}

    client = TestClient(app)
    res = client.post(
        "/login",
        content="select * from users",
        headers={"User-Agent": "Mozilla/5.0", "x-user-id": "u2"},
    )
    assert res.status_code == 200
    assert seen == ["flag"]
