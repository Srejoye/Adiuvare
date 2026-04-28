from collections import Counter
from typing import cast

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static

from ..widgets.risk_stream import RiskStream
from ..workspace import PALETTE, WorkspaceView


class MonitorScreen(WorkspaceView):
    shortcut_hints = "[1-6] tabs  [up/down] rows  [r] refresh  [q] quit"
    primary_id = "monitor-stream"

    def compose(self) -> ComposeResult:
        with Horizontal(id="monitor-shell"):
            with Vertical(classes="monitor-main"):
                yield Static("MONITOR", id="monitor-title")
                yield RiskStream(id="monitor-stream")
            with Vertical(classes="monitor-side"):
                yield Static("", id="runtime-profile")
                yield Static("", id="runtime-snapshot")
                yield Static("", id="runtime-counts")

    def on_mount(self) -> None:
        self.refresh_view()

    def refresh_view(self) -> None:
        rows = self._app().recent_rows(14)
        counts = Counter(str(row.get("verdict", "allow")) for row in rows)
        self.query_one("#monitor-stream", RiskStream).show_events(rows)
        self.query_one("#runtime-profile", Static).update(self._profile_text())
        self.query_one("#runtime-snapshot", Static).update(self._snapshot_text())
        self.query_one("#runtime-counts", Static).update(self._counts_text(counts, len(rows)))

    def footer_status(self) -> str:
        snap = self._app().runtime_snapshot()
        return f"{snap.get('framework', 'app')} / {snap.get('strictness', 'internal')} profile"

    def _profile_text(self) -> str:
        snap = self._app().runtime_snapshot()
        lines = [
            "profile",
            f"framework: {snap.get('framework', 'fastapi')}",
            f"instances: {snap.get('instances', 'single')}",
            f"strictness: {snap.get('strictness', 'internal')}",
            f"backend: {snap.get('backend', 'sqlite')}",
            f"ai mode: {snap.get('ai_mode', 'off')}",
            f"ai model: {snap.get('ai_model', 'llama3')}",
        ]
        return "\n".join(lines)

    def _snapshot_text(self) -> str:
        snap = self._app().runtime_snapshot()
        state_db = str(snap.get("state_db", "-"))
        audit_db = str(snap.get("audit_db", "-"))
        ai_mode = str(snap.get("ai_mode", "off"))
        ai_enabled = bool(snap.get("ai_enabled", False))
        observe = bool(snap.get("observe_only", False))
        recent = int(snap.get("recent_events", 0))
        wl = int(snap.get("whitelist_size", 0))
        live = bool(snap.get("connected", False))
        lines = [
            "runtime snapshot",
            f"live link: {live}",
            f"ai mode: {ai_mode}",
            f"ai enabled: {ai_enabled}",
            f"observe only: {observe}",
            f"recent stream: {recent}",
            f"whitelist: {wl}",
            f"audit db: {audit_db}",
            f"state db: {state_db}",
        ]
        return "\n".join(lines)

    def _counts_text(self, counts: Counter[str], total: int) -> str:
        snap = self._app().runtime_snapshot()
        lines = [
            "thresholds and weights",
            f"flag: {float(snap.get('flag_threshold', 0.25)):0.2f}",
            f"throttle: {float(snap.get('throttle_threshold', 0.55)):0.2f}",
            f"block: {float(snap.get('block_threshold', 0.80)):0.2f}",
            f"payload wt: {float(snap.get('payload_weight', 0.40)):0.2f}",
            f"behavior wt: {float(snap.get('behavior_weight', 0.35)):0.2f}",
            f"identity wt: {float(snap.get('identity_weight', 0.25)):0.2f}",
            "",
            "recent decisions",
            f"allow: {counts.get('allow', 0)}",
            f"flag: {counts.get('flag', 0)}",
            f"throttle: {counts.get('throttle', 0)}",
            f"block: {counts.get('block', 0)}",
            f"rows: {total}",
        ]
        return "\n".join(lines)

    def _app(self):
        return cast("AdiuvareApp", self.app)
