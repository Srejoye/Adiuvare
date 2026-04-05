from pathlib import Path
from typing import Any

from .config import build_snapshot, load_config
from .core.events import EventHooks
from .core.models import RequestContext
from .core.pipeline import Pipeline
from .state.identity_store import IdentityStore


class Guard:
    def __init__(
        self,
        preset: str = "balanced",
        config_path: str | Path | None = None,
        soft_signals: list | None = None,
    ) -> None:
        self._cfg = load_config(config_path, preset=preset)
        self._cfg_snap = build_snapshot(self._cfg)
        self._id_store = IdentityStore()
        self._pipeline = Pipeline(self._id_store, soft_signals=soft_signals)
        self._hooks = EventHooks()

    @property
    def hooks(self) -> EventHooks:
        return self._hooks

    async def inspect(self, ctx: RequestContext):
        if ctx.snapshot is None:
            ctx.snapshot = self._cfg_snap

        gate, event = await self._pipeline.process(ctx)
        if not gate.passed:
            self._hooks.emit_block(gate)
            return gate, None

        if event is not None:
            self._hooks.emit_event(event)
        return gate, event

    def handle(self, ctx: RequestContext):
        return self.inspect(ctx)

    def use(self, app: Any, framework: str = "fastapi") -> None:
        if framework == "fastapi":
            from .integrations.fastapi import AdiuvareMiddleware

            app.add_middleware(AdiuvareMiddleware, guard=self)
            return

        raise ValueError(f"unsupported framework: {framework}")
