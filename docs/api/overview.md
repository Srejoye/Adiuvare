# API Overview

Adiuvare has more internal modules than public API. The public surface is
smaller on purpose, and sticking to it will make upgrades much less painful.

## Quick example

Most application code starts here:

```python
from adiuvare import Guard
from adiuvare.config import load_config
from adiuvare.signals import HardSignal, SoftSignal
from adiuvare.core.models import RequestContext, SignalResult
from adiuvare.policies import RoutePolicy
```

If you only use built-in signals and built-in route policies, it can be even
smaller:

```python
from adiuvare import Guard
```

## Stable public surface

For `0.1.0`, these are the safest public entry points:

- `adiuvare.Guard`
- `adiuvare.__version__`
- `adiuvare.config`
- `adiuvare.signals`
- `adiuvare.core.models`
- `adiuvare.policies`
- the `adv` CLI

Those are the surfaces backed by the reference pages in `docs/api/`.

## Public reference pages

- [Guard API](guard.md)
- [Config API](config.md)
- [Signals API](signals.md)
- [Models API](models.md)

## Public surface by job

### App setup

Reach for:

- `Guard(...)`
- `Guard.from_config(...)`
- `Guard.auto(...)`
- `guard.use(...)`

```python
from fastapi import FastAPI

from adiuvare import Guard

app = FastAPI()
guard = Guard.from_config("adiuvare.yaml")
guard.use(app, framework="fastapi")
```

### Configuration

Reach for:

- `load_config(...)`
- `AdiuvareConfig`
- `PRESETS`

```python
from adiuvare.config import load_config

cfg = load_config("adiuvare.yaml")
print(cfg.thresholds.block)
```

```text
0.8
```

### Route behavior

Reach for:

- `guard.policy(...)`
- `guard.protect(...)`
- `guard.exempt()`
- `guard.configure_routes(...)`
- `RoutePolicy`

### Extension points

Reach for:

- `SoftSignal`
- `HardSignal`
- `PayloadSignal`
- `validate_hard_signal(...)`

Use [Built-in signals](../signals.md) when you want the conceptual guide to the
default signal families. Use [Signals API](signals.md) when you need the class
reference.

### Runtime inspection

Reach for:

- `guard.check(...)`
- `guard.check_sync(...)`
- `guard.hooks`
- `adv status`
- `adv logs`
- `adv`

## Advanced but still public

These are real public methods, but they are not where most teams should start:

- `guard.startbgtasks()`
- `guard.ensure_started()`
- `guard.shutdown()`
- `guard.checkpoint()`
- `guard.runtimesnapshot()`

They are useful for advanced integrations, tests, and custom runtime control.

## Internal modules

Do not build long-lived app code directly on these unless you want to own the
maintenance cost:

- `adiuvare.core.scorer`
- `adiuvare.core.verdict`
- `adiuvare.core.pipeline`
- `adiuvare.core.policy_engine`
- `adiuvare.state.*`
- `adiuvare.tui.*`
- most framework middleware classes directly

## Related

- [Quickstart](../quickstart.md)
- [Guard API](guard.md)
- [Config API](config.md)
- [Signals API](signals.md)
