from dataclasses import dataclass
from typing import Literal


@dataclass
class RoutePolicy:
    """Bundle the default route posture the decorators and config can reuse."""

    sensitivity: Literal["public", "internal", "critical"] = "internal"
    ai_mode: Literal["off", "assist", "critical", "async"] = "off"
    trackB: bool = True
    sink_mode: str = "off"

    def with_overrides(self, **overrides):
        data = {
            "sensitivity": self.sensitivity,
            "ai_mode": self.ai_mode,
            "trackB": self.trackB,
            "sink_mode": self.sink_mode,
        }
        data.update(overrides)
        return RoutePolicy(**data)
