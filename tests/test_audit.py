import json
import sqlite3

from adiuvare.core.models import AdiuvareEvent
from adiuvare.state.audit_log import AuditLog
from adiuvare.state.identity_store import IdentityStore
from adiuvare.state.persistence import init_state_db, save_identity_state


def test_audit_log_writes_event(tmp_path):
    db_path = tmp_path / "audit.db"
    log = AuditLog(db_path)
    event = AdiuvareEvent(
        identity="u1",
        endpoint="/login",
        score=0.42,
        verdict="flag",
        breakdown={"payload": 0.28, "identity": 0.14},
    )

    log.write(event)

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "select identity, verdict, breakdown_json from audit_events"
        ).fetchone()

    assert row is not None
    assert row[0] == "u1"
    assert row[1] == "flag"
    assert json.loads(row[2])["payload"] == 0.28


def test_state_checkpoint_writes_identity_window(tmp_path):
    db_path = tmp_path / "audit.db"
    store = IdentityStore()
    win = store.get("u1")
    win.seen = 3
    win.score_ewma = 0.42
    store.update("u1", win)

    init_state_db(db_path)
    save_identity_state(db_path, store)

    with sqlite3.connect(db_path) as conn:
        row = conn.execute(
            "select identity, seen, score_ewma from identity_state"
        ).fetchone()

    assert row == ("u1", 3, 0.42)
