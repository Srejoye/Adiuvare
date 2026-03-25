from adiuvare.core.gate import run_trackA
from adiuvare.core.models import RequestContext
from adiuvare.state.identity_store import IdentityStore


def test_gate_passes_clean_identity():
    ctx = RequestContext(
        identity="u1",
        payload=None,
        url="/",
        method="GET",
        headers={},
        ip="127.0.0.1",
        endpoint="/",
    )

    res = run_trackA(ctx, IdentityStore())
    assert res.passed is True


def test_gate_blocks_blocked_identity():
    store = IdentityStore()
    store.block("u1")

    ctx = RequestContext(
        identity="u1",
        payload=None,
        url="/",
        method="GET",
        headers={},
        ip="127.0.0.1",
        endpoint="/",
    )

    res = run_trackA(ctx, store)
    assert res.passed is False
    assert res.status_code == 429
