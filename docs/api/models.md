# Models API

These are the small data objects that move through Adiuvare's runtime. You
usually meet them in custom signals, manual `guard.check(...)` calls, hooks,
audit output, and debugging.

## Quick example

```python
from adiuvare.core.models import ConfigSnapshot, RequestContext

snap = ConfigSnapshot(
    payload_weight=0.40,
    behavior_weight=0.35,
    identity_weight=0.25,
    flag_threshold=0.25,
    throttle_threshold=0.55,
    block_threshold=0.80,
)

ctx = RequestContext(
    identity="user:42",
    payload="' OR 'a'='a",
    url="/search?q=test",
    method="POST",
    headers={"user-agent": "curl/8.0"},
    ip="127.0.0.1",
    endpoint="/search",
    snapshot=snap,
)

print(ctx.identity)
print(ctx.snapshot.block_threshold)
print(ctx.endpoint)
```

```text
user:42
0.8
/search
```

## ConfigSnapshot

```python
ConfigSnapshot(
    payload_weight: float,
    behavior_weight: float,
    identity_weight: float,
    flag_threshold: float,
    throttle_threshold: float,
    block_threshold: float,
    observe_only: bool = False,
    ai_mode: str = "off",
)
```

This is the small request-time snapshot the scorer and signals read.

| field | meaning |
| --- | --- |
| `payload_weight` | how strongly payload findings matter |
| `behavior_weight` | how strongly behavior findings matter |
| `identity_weight` | how strongly identity memory matters |
| `flag_threshold` | first noteworthy score band |
| `throttle_threshold` | throttle score band |
| `block_threshold` | block score band |
| `observe_only` | softer runtime posture |
| `ai_mode` | request-time AI mode |

> `context` and `ip_rep` still use fixed built-in weights. There are no
> `context_weight` or `ip_rep_weight` fields here yet.

## RequestContext

```python
RequestContext(
    identity: str,
    payload: str | None,
    url: str,
    method: str,
    headers: dict[str, str],
    ip: str,
    endpoint: str,
    sensitivity: Literal["public", "internal", "critical"] = "internal",
    snapshot: ConfigSnapshot | None = None,
)
```

This is the primary request object used by signals, gates, and manual
inspection paths.

The fields you will read most often are:

- `identity`
- `payload`
- `headers`
- `ip`
- `endpoint`
- `sensitivity`
- `snapshot`

Example:

```python
from adiuvare.core.models import RequestContext

ctx = RequestContext(
    identity="worker:nightly",
    payload=None,
    url="/cron/nightly",
    method="INTERNAL",
    headers={},
    ip="127.0.0.1",
    endpoint="/cron/nightly",
    sensitivity="critical",
)

print(ctx.method)
print(ctx.sensitivity)
```

```text
INTERNAL
critical
```

## SignalResult

```python
SignalResult(
    score: float,
    reason: str,
    detail: dict[str, Any] = {},
    exception: Exception | None = None,
)
```

This is what `SoftSignal.extract(...)` returns.

| field | meaning |
| --- | --- |
| `score` | how much risk this signal contributes |
| `reason` | short label for the branch that fired |
| `detail` | optional structured metadata for later debugging or UI display |
| `exception` | optional captured exception |

Example:

```python
from adiuvare.core.models import SignalResult

res = SignalResult(
    score=0.42,
    reason="tenant_header",
    detail={"header": "x-tenant", "value": "red-team"},
)

print(res.score)
print(res.reason)
print(res.detail["value"])
```

```text
0.42
tenant_header
red-team
```

## AdiuvareEvent

```python
AdiuvareEvent(
    identity: str,
    endpoint: str,
    score: float,
    verdict: str,
    breakdown: dict[str, float],
    ip: str = "",
    detail: dict[str, Any] = {},
    logged_verdict: str | None = None,
)
```

This is the scored event produced by `trackB`.

| field | meaning |
| --- | --- |
| `identity` | identity string associated with the event |
| `endpoint` | normalized endpoint where the event happened |
| `score` | final combined score |
| `verdict` | runtime outcome such as `allow`, `flag`, `throttle`, or `block` |
| `breakdown` | per-signal score contributions |
| `ip` | client IP when the integration path provides one |
| `detail` | extra structured metadata |
| `logged_verdict` | optional persisted/log-friendly verdict label |

Example:

```python
from adiuvare.core.models import AdiuvareEvent

event = AdiuvareEvent(
    identity="u1",
    endpoint="/login",
    score=0.42,
    verdict="flag",
    breakdown={"payload": 0.28, "identity": 0.14},
    ip="203.0.113.4",
)

print(event.verdict)
print(event.breakdown["payload"])
```

```text
flag
0.28
```

## PolicyDecision

```python
PolicyDecision(
    verdict: str,
    logged: str,
)
```

This is the small result object used around the final verdict mapping path.

Example:

```python
from adiuvare.core.models import PolicyDecision

decision = PolicyDecision(verdict="throttle", logged="flag")

print(decision.verdict)
print(decision.logged)
```

```text
throttle
flag
```

## RoutePolicy

```python
RoutePolicy(
    sensitivity: Literal["public", "internal", "critical"] = "internal",
    ai_mode: Literal["off", "assist", "critical", "async"] = "off",
    trackB: bool = True,
    sink_mode: str = "off",
)
```

`RoutePolicy` lives in `adiuvare.policies`, but it belongs here because it is
part of the same public data surface.

| field | meaning |
| --- | --- |
| `sensitivity` | `public`, `internal`, or `critical` |
| `ai_mode` | `off`, `assist`, `critical`, or `async` |
| `trackB` | whether the scoring path should run |
| `sink_mode` | how sink hooks should behave |

You will usually meet it behind:

- `@guard.policy("admin")`
- `@guard.protect(...)`
- `guard.configure_routes(...)`

Example:

```python
from adiuvare.policies import RoutePolicy

base = RoutePolicy(sensitivity="critical", ai_mode="assist", sink_mode="inline")
search_variant = base.with_overrides(sensitivity="public", ai_mode="off")

print(base.sensitivity, base.ai_mode)
print(search_variant.sensitivity, search_variant.ai_mode)
```

```text
critical assist
public off
```

## Related

- [Guard API](guard.md)
- [Signals API](signals.md)
- [Route policies](../extending/route-policies.md)
