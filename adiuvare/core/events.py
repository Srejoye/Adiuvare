from collections.abc import Callable
from typing import Any

from .gate import GateResult
from .models import AdiuvareEvent


class EventHooks:
    def __init__(self) -> None:
        self._event_handlers: list[Callable[[AdiuvareEvent], Any]] = []
        self._block_handlers: list[Callable[[GateResult], Any]] = []

    def on_event(self, fn: Callable[[AdiuvareEvent], Any]) -> Callable[[AdiuvareEvent], Any]:
        self._event_handlers.append(fn)
        return fn

    def on_block(self, fn: Callable[[GateResult], Any]) -> Callable[[GateResult], Any]:
        self._block_handlers.append(fn)
        return fn

    def emit_event(self, event: AdiuvareEvent) -> None:
        for fn in self._event_handlers:
            fn(event)

    def emit_block(self, gate: GateResult) -> None:
        for fn in self._block_handlers:
            fn(gate)
