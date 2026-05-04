import json
import sqlite3
from pathlib import Path

from ..core.models import AdiuvareEvent


class AuditLog:
    """Write scored events and control-plane patches into the local SQLite audit store."""

    def __init__(self, db_path: str | Path) -> None:
        self._db_path = str(db_path)
        self._init_db()

    def _init_db(self) -> None:
        schema = Path(__file__).with_name("schema.sql").read_text()
        with sqlite3.connect(self._db_path) as conn:
            conn.executescript(schema)

    def write(self, event: AdiuvareEvent) -> None:
        """Persist one event, copying its IP into detail when older readers expect it there."""

        detail = dict(event.detail)
        if event.ip and not detail.get("ip"):
            detail["ip"] = event.ip
        row = (
            event.identity,
            event.endpoint,
            event.score,
            event.verdict,
            json.dumps(event.breakdown),
            json.dumps(detail),
        )
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                insert into audit_events (
                    identity,
                    endpoint,
                    score,
                    verdict,
                    breakdown_json,
                    detail_json
                ) values (?, ?, ?, ?, ?, ?)
                """,
                row,
            )
            conn.commit()

    def recent(self, limit: int = 20) -> list[dict]:
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                """
                select identity, endpoint, score, verdict, breakdown_json, detail_json, created_at
                from audit_events
                order by id desc
                limit ?
                """,
                (limit,),
            ).fetchall()

        return [self._row_dict(row) for row in rows]

    def by_identity(self, identity: str, limit: int = 20) -> list[dict]:
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                """
                select identity, endpoint, score, verdict, breakdown_json, detail_json, created_at
                from audit_events
                where identity = ?
                order by id desc
                limit ?
                """,
                (identity, limit),
            ).fetchall()

        return [self._row_dict(row) for row in rows]

    def window(self, days: int = 7, limit: int = 500) -> list[dict]:
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                """
                select identity, endpoint, score, verdict, breakdown_json, detail_json, created_at
                from audit_events
                where created_at >= datetime('now', ?)
                order by id desc
                limit ?
                """,
                (f"-{int(days)} days", int(limit)),
            ).fetchall()

        return [self._row_dict(row) for row in rows]

    def write_patch(self, kind: str, patch: dict) -> None:
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                insert into config_history (kind, patch_json)
                values (?, ?)
                """,
                (kind, json.dumps(patch)),
            )
            conn.commit()

    def history(self, limit: int = 50) -> list[dict]:
        """Return recent control-plane patches in reverse chronological order."""

        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                """
                select kind, patch_json, created_at
                from config_history
                order by id desc
                limit ?
                """,
                (int(limit),),
            ).fetchall()

        out: list[dict] = []
        for kind, patch_json, created_at in rows:
            try:
                patch = json.loads(patch_json)
            except json.JSONDecodeError:
                patch = patch_json
            out.append(
                {
                    "kind": str(kind),
                    "patch": patch,
                    "created_at": created_at,
                }
            )
        return out

    def _row_dict(self, row) -> dict:
        detail = json.loads(row[5])
        ip = ""
        if isinstance(detail, dict):
            ip = str(detail.get("ip", "") or "")
        if not ip and isinstance(row[0], str) and row[0].startswith("ip:"):
            ip = row[0].split(":", 1)[1]
        return {
            "identity": row[0],
            "endpoint": row[1],
            "score": row[2],
            "verdict": row[3],
            "breakdown": json.loads(row[4]),
            "detail": detail,
            "ip": ip,
            "created_at": row[6],
        }
