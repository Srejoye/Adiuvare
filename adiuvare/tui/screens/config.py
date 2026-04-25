from pathlib import Path
from typing import cast

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input, Static

from ..workspace import WorkspaceView


class ConfigScreen(WorkspaceView):
    shortcut_hints = "[1-6] tabs  [s] save  [r] reset  [t] observe"
    primary_id = "cfg-block"

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._observe = False

    def compose(self) -> ComposeResult:
        with Vertical():
            yield Static("config patching")
            yield Static("block threshold", id="cfg-block-label")
            yield Input(id="cfg-block")
            yield Static("ai mode", id="cfg-ai-label")
            yield Input(id="cfg-ai")
            with Horizontal():
                yield Button("Toggle observe", id="cfg-toggle")
                yield Button("Save", id="cfg-save")
                yield Button("Reset", id="cfg-reset")
            yield Static("", id="cfg-summary")

    def on_mount(self) -> None:
        self.refresh_view()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cfg-toggle":
            self._observe = not self._observe
            self._render_summary("observe flag changed")
        elif event.button.id == "cfg-save":
            self.action_save_config()
        elif event.button.id == "cfg-reset":
            self.action_reset_config()

    def action_save_config(self) -> None:
        block = float(self.query_one("#cfg-block", Input).value)
        ai_mode = self.query_one("#cfg-ai", Input).value.strip() or "off"
        changes = {
            "thresholds": {"block": block},
            "runtime": {"observe_only": self._observe},
            "ai": {"mode": ai_mode, "enabled": ai_mode != "off"},
        }
        self._app().save_config(changes)
        self.refresh_view()
        self._app().set_footer_status("config saved")

    def action_reset_config(self) -> None:
        self.refresh_view()
        self._app().set_footer_status("config reset")

    def refresh_view(self) -> None:
        cfg = self._app().config
        self._observe = cfg.runtime.observe_only
        self.query_one("#cfg-block", Input).value = str(cfg.thresholds.block)
        self.query_one("#cfg-ai", Input).value = cfg.ai.mode
        self._render_summary("editing local config")

    def footer_status(self) -> str:
        path = self._app().config_path or str(Path("adiuvare.yaml"))
        strict = self._app().config.meta.strictness
        return f"config path: {path} | strictness: {strict}"

    def _render_summary(self, note: str) -> None:
        cfg = self._app().config
        self.query_one("#cfg-summary", Static).update(
            "\n".join(
                [
                    f"framework: {cfg.meta.framework}",
                    f"strictness: {cfg.meta.strictness}",
                    f"observe only: {self._observe}",
                    f"ai mode: {cfg.ai.mode}",
                    f"flag/throttle/block: {cfg.thresholds.flag:.2f} / {cfg.thresholds.throttle:.2f} / {cfg.thresholds.block:.2f}",
                    f"state db: {cfg.runtime.state_db_path}",
                    note,
                ]
            )
        )

    def _app(self):
        return cast("AdiuvareApp", self.app)
