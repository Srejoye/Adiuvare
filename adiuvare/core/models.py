from dataclasses import dataclass, field
from typing import Any, Literal


@dataclass
class ConfigSnapshot:
    """Carry the scoring and gate settings that need to travel with a request."""

    payload_weight: float
    behavior_weight: float
    identity_weight: float
    flag_threshold: float
    throttle_threshold: float
    block_threshold: float
    observe_only: bool = False
    ai_mode: str = "off"


@dataclass
class RequestContext:
    """Describe the request data the guard and signals inspect."""

    identity: str
    payload: str | None
    url: str
    method: str
    headers: dict[str, str]
    ip: str
    endpoint: str
    sensitivity: Literal["public", "internal", "critical"] = "internal"
    snapshot: ConfigSnapshot | None = None


@dataclass
class SignalResult:
    """Carry one signal's score, reason, and optional debug detail."""

    score: float
    reason: str
    detail: dict[str, Any] = field(default_factory=dict)
    exception: Exception | None = None


@dataclass
class AdiuvareEvent:
    """Record the final scored event that gets emitted and persisted."""

    identity: str
    endpoint: str
    score: float
    verdict: str
    breakdown: dict[str, float]
    ip: str = ""
    detail: dict[str, Any] = field(default_factory=dict)
    logged_verdict: str | None = None


@dataclass
class PolicyDecision:
    """Hold the enforced verdict and the verdict that should be logged."""

    verdict: str
    logged: str
