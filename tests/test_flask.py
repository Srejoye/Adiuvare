from flask import Flask, jsonify, request

from adiuvare import Guard


def test_flask_middleware_allows_clean_request():
    app = Flask(__name__)
    guard = Guard()
    guard.use(app, framework="flask")

    @app.get("/ping")
    def ping():
        assert request.environ.get("adiuvare.event") is not None
        return jsonify(ok=True)

    client = app.test_client()
    res = client.get("/ping", headers={"User-Agent": "Mozilla/5.0", "x-user-id": "u1"})
    assert res.status_code == 200
    assert res.get_json() == {"ok": True}


def test_flask_middleware_blocks_when_identity_is_blocked():
    app = Flask(__name__)
    guard = Guard()
    guard._id_store.set_blocked("u1", 60)
    guard.use(app, framework="flask")

    @app.get("/ping")
    def ping():
        return jsonify(ok=True)

    client = app.test_client()
    res = client.get("/ping", headers={"User-Agent": "Mozilla/5.0", "x-user-id": "u1"})
    assert res.status_code == 429
