# Config API

This is the public config surface you are actually meant to code against. Most
people will use `load_config()` and inspect the resulting `AdiuvareConfig`.

## Quick example

```python
from adiuvare.config import load_config

cfg = load_config("adiuvare.yaml")

print(cfg.runtime.backend)
print(cfg.thresholds.block)
print(cfg.ai.mode)
```

```text
sqlite
0.8
off
```

## Public imports

```python
from adiuvare.config import (
    AdiuvareConfig,
    PRESETS,
    SignalWeights,
    Thresholds,
    build_snapshot,
    find_config_file,
    load_config,
)
```

## load_config()

```python
load_config(path: str | Path | None = None, preset: str = "balanced") -> AdiuvareConfig
```

`path` lets you point at a specific YAML file. If you leave it as `None`,
Adiuvare uses config discovery. `preset` selects the base config before the
file is merged in.

Load order:

1. deep-copy the selected preset
2. resolve a config file
3. merge YAML if a file exists
4. apply environment overrides
5. validate through the Pydantic models

If `path` is omitted, discovery checks:

1. `ADIUVARE_CONFIG`
2. the nearest `adiuvare.yaml` upward from the current directory
3. `~/adiuvare.yaml`
4. no file at all, which leaves the preset as the base

Example:

```python
from adiuvare.config import load_config

cfg = load_config("adiuvare.yaml")
print(cfg.meta.framework)
print(cfg.runtime.observe_only)
```

```text
fastapi
True
```

Strict preset with no file:

```python
from adiuvare.config import load_config

cfg = load_config(preset="strict")
print(cfg.thresholds.block)
print(cfg.ai.mode)
```

```text
0.7
assist
```

If you pass a missing explicit path, `load_config()` raises `FileNotFoundError`.

## find_config_file()

```python
find_config_file(
    start_dir: str | Path | None = None,
    *,
    include_home: bool = True,
    use_env: bool = True,
) -> Path | None
```

Use this when you want to know which config file Adiuvare would pick if you did
not pass one explicitly.

Example:

```python
from adiuvare.config import find_config_file

cfg_path = find_config_file(r"H:\projects\billing\app\jobs")
print(cfg_path)
```

```text
H:\projects\billing\adiuvare.yaml
```

## build_snapshot()

```python
build_snapshot(cfg: AdiuvareConfig) -> ConfigSnapshot
```

This converts the full config object into the smaller request-time snapshot
used by the scorer and signals.

Example:

```python
from adiuvare.config import build_snapshot, load_config

cfg = load_config("adiuvare.yaml")
snap = build_snapshot(cfg)

print(snap.payload_weight)
print(snap.block_threshold)
print(snap.ai_mode)
```

```text
0.4
0.8
off
```

## AdiuvareConfig

`AdiuvareConfig` is the top-level configuration object returned by
`load_config()`.

Fields:

- `weights`
- `thresholds`
- `runtime`
- `ai`
- `meta`

Example:

```python
from adiuvare.config import AdiuvareConfig

cfg = AdiuvareConfig()
cfg.runtime.observe_only = True
cfg.ai.mode = "assist"

print(cfg.model_dump())
```

## SignalWeights

`SignalWeights` covers the three user-tunable soft-signal families.

| field | default | meaning |
| --- | --- | --- |
| `payload` | `0.40` | how much payload findings matter |
| `behavior` | `0.35` | how much behavior and rate history matter |
| `identity` | `0.25` | how much identity memory matters |

Each value is validated between `0.0` and `1.0`.

Example:

```python
from adiuvare.config import SignalWeights

weights = SignalWeights(payload=0.50, behavior=0.30, identity=0.20)
print(weights)
```

```text
SignalWeights(payload=0.5, behavior=0.3, identity=0.2)
```

> `context` and `ip_rep` still use fixed built-in weights. They are not fields
> on `SignalWeights` today.

## Thresholds

`Thresholds` holds the three verdict bands.

| field | default | meaning |
| --- | --- | --- |
| `flag` | `0.25` | first noteworthy score band |
| `throttle` | `0.55` | score band where traffic starts getting slowed or suppressed |
| `block` | `0.80` | score band where a request becomes block-worthy |

Validation enforces:

```text
flag <= throttle <= block
```

Example:

```python
from adiuvare.config import Thresholds

thresholds = Thresholds(flag=0.20, throttle=0.50, block=0.75)
print(thresholds.block)
```

```text
0.75
```

## runtime

These fields live on `cfg.runtime`.

| field | default | meaning |
| --- | --- | --- |
| `backend` | `sqlite` | `memory`, `sqlite`, or `redis` |
| `audit_db_path` | `.adiuvare/audit.db` | SQLite audit database path |
| `state_db_path` | `.adiuvare/state.db` | SQLite checkpoint database path |
| `redis_url` | `None` | Redis connection URL |
| `observe_only` | `False` | softer observation posture |
| `monitored_window` | `20` | default request count for monitored identities |
| `monitored_multiplier` | `1.2` | multiplier while an identity is monitored |

Example:

```yaml
runtime:
  backend: redis
  redis_url: redis://127.0.0.1:6379/0
```

## ai

These fields live on `cfg.ai`.

| field | default | meaning |
| --- | --- | --- |
| `enabled` | `False` | convenience flag for whether AI is effectively on |
| `mode` | `off` | `off`, `assist`, `critical`, or `async` |
| `model` | `llama3` | external model name |
| `base_url` | `http://127.0.0.1:11434` | Ollama-compatible API base URL |
| `api_key` | `None` | optional authentication value |
| `timeout_secs` | `5.0` | how long to wait before degrading cleanly |

Example:

```yaml
ai:
  enabled: true
  mode: assist
  model: mistral
  base_url: http://127.0.0.1:11434
  timeout_secs: 10.0
```

## meta

These fields live on `cfg.meta`.

| field | default | meaning |
| --- | --- | --- |
| `framework` | `fastapi` | descriptive framework hint |
| `instances` | `single` | deployment hint such as `single` or `multi` |
| `strictness` | `internal` | descriptive posture hint used by starter flows and presets |

## PRESETS

Two presets ship today:

- `balanced`
- `strict`

Example:

```python
from adiuvare.config import PRESETS

balanced = PRESETS["balanced"]
strict = PRESETS["strict"]

print(balanced.thresholds.block)
print(strict.thresholds.block)
```

```text
0.8
0.7
```

## Environment overrides

Current env hooks:

- `ADIUVARE_AI_MODE`
- `ADIUVARE_AI_BASE_URL`
- `ADIUVARE_OLLAMA_URL`
- `ADIUVARE_AI_MODEL`
- `ADIUVARE_AI_API_KEY`
- `ADIUVARE_AI_TIMEOUT_SECS`
- `ADIUVARE_REDIS_URL`
- `ADIUVARE_OBSERVE_ONLY`
- `ADIUVARE_BLOCK_THRESHOLD`

Example:

```bash
export ADIUVARE_AI_MODE=assist
export ADIUVARE_BLOCK_THRESHOLD=0.72
```

```python
from adiuvare.config import load_config

cfg = load_config("adiuvare.yaml")
print(cfg.ai.mode)
print(cfg.thresholds.block)
```

```text
assist
0.72
```

## Related

- [Configuration guide](../configuration.md)
- [Guard API](guard.md)
