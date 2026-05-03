# Configuration

Adiuvare loads config in a predictable order, then applies a small set of
environment overrides. Once you know that order, the rest of the file is pretty
easy to reason about.

## Quick example

```python
from adiuvare.config import find_config_file, load_config

print(find_config_file())
cfg = load_config()
print(cfg.runtime.backend)
print(cfg.ai.mode)
```

```text
H:\projects\billing\adiuvare.yaml
sqlite
off
```

## Discovery order

If you do not pass a config path explicitly, Adiuvare resolves config in this
order:

1. explicit path from your code
2. `ADIUVARE_CONFIG`
3. the nearest `adiuvare.yaml` from the current working directory upward
4. `~/adiuvare.yaml`
5. preset defaults if no file exists

That same logic is used by the library, the CLI, and the TUI entry flow.

### Example: nearest project config wins

```text
workspace/
  adiuvare.yaml
  services/
    billing/
      scripts/
```

From `workspace/services/billing/scripts`:

```python
from adiuvare.config import find_config_file, load_config

print(find_config_file())
cfg = load_config()
print(cfg.meta.framework)
```

```text
workspace\adiuvare.yaml
fastapi
```

### Example: force a specific file

```bash
export ADIUVARE_CONFIG=/srv/tenant-a/adiuvare.yaml
adv status
```

```text
config: /srv/tenant-a/adiuvare.yaml
runtime: offline
framework: flask
instances: single
observe_only: False
ai_mode: off
audit_db: .adiuvare/audit.db
```

### Nested config warning in `adv init`

If you run `adv init` inside a subfolder of a project that already has an
`adiuvare.yaml` higher up the tree, the CLI warns before creating a second
config root.

```text
found existing config at H:\repo\adiuvare.yaml - create another one at H:\repo\services\billing\adiuvare.yaml? [y/N]
```

## Starter file

```yaml
weights:
  payload: 0.40
  behavior: 0.35
  identity: 0.25

thresholds:
  flag: 0.25
  throttle: 0.55
  block: 0.80

runtime:
  backend: sqlite
  audit_db_path: .adiuvare/audit.db
  state_db_path: .adiuvare/state.db
  redis_url:
  observe_only: false
  monitored_window: 20
  monitored_multiplier: 1.2

ai:
  enabled: false
  mode: off
  model: llama3
  base_url: http://127.0.0.1:11434
  api_key:
  timeout_secs: 5.0

meta:
  framework: fastapi
  instances: single
  strictness: internal
```

If you only want the smallest working file:

```yaml
runtime:
  audit_db_path: .adiuvare/audit.db
  state_db_path: .adiuvare/state.db
```

The preset fills in the rest.

## weights

These are the user-tunable soft-signal families.

| field | meaning |
| --- | --- |
| `payload` | how much payload findings matter |
| `behavior` | how much request-shape and rate history matter |
| `identity` | how much identity memory matters |

Adiuvare also has built-in `context` and `ip_rep` signals, but those still use
fixed internal weights.

## thresholds

These are the three decision bands:

| field | meaning |
| --- | --- |
| `flag` | first score band where a request becomes noteworthy |
| `throttle` | band where traffic starts getting slowed or suppressed |
| `block` | band where a request becomes block-worthy |

The validator enforces:

```text
flag <= throttle <= block
```

## runtime

| field | meaning |
| --- | --- |
| `backend` | `memory`, `sqlite`, or `redis` |
| `audit_db_path` | local SQLite audit database path |
| `state_db_path` | local state checkpoint database path |
| `redis_url` | Redis connection URL when `backend: redis` |
| `observe_only` | softer posture for watching traffic first |
| `monitored_window` | default request count for monitored identities |
| `monitored_multiplier` | score multiplier while an identity is monitored |

### backend

Use `sqlite` for the normal local single-instance setup. Use `redis` when you
want Redis-backed event transport, even for one running app.

> `redis` is a supported backend. It does not automatically mean full
> multi-instance distributed coordination.

Example:

```yaml
runtime:
  backend: redis
  redis_url: redis://127.0.0.1:6379/0
```

## ai

| field | meaning |
| --- | --- |
| `enabled` | convenience flag for whether AI is effectively on |
| `mode` | `off`, `assist`, `critical`, or `async` |
| `model` | model name passed to the endpoint |
| `base_url` | Ollama-compatible base URL |
| `api_key` | optional API key for endpoints that need one |
| `timeout_secs` | how long to wait before degrading cleanly |

The real connection knobs are:

- `ai.model`
- `ai.base_url`
- `ai.api_key`
- `ai.timeout_secs`

Example:

```yaml
ai:
  enabled: true
  mode: assist
  model: llama3
  base_url: http://127.0.0.1:11434
  timeout_secs: 10.0
```

The model does not have to be `llama3`. Any Ollama-compatible model exposed by
your endpoint is fair game.

## meta

| field | meaning |
| --- | --- |
| `framework` | descriptive framework hint used by setup and operator views |
| `instances` | deployment hint such as `single` or `multi` |
| `strictness` | descriptive posture hint used by starter flows and presets |

`single` is still the honest default today. Treat `multi` as a deployment hint,
not as proof that full shared distributed state is solved.

## Presets

Two presets ship today:

- `balanced`
- `strict`

The loader starts from the preset, then merges YAML, then applies environment
overrides.

```python
from adiuvare.config import load_config

cfg = load_config("adiuvare.yaml", preset="strict")
print(cfg.thresholds.block)
```

```text
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
export ADIUVARE_AI_BASE_URL=http://127.0.0.1:11434
export ADIUVARE_AI_MODEL=llama3
export ADIUVARE_BLOCK_THRESHOLD=0.72
```

```python
from adiuvare.config import load_config

cfg = load_config("adiuvare.yaml")
print(cfg.ai.mode)
print(cfg.ai.model)
print(cfg.thresholds.block)
```

```text
assist
llama3
0.72
```

## Live patching and saved config

Not every field behaves the same way while the app is already running.

These are the best live-patch candidates when the runtime is connected:

- `thresholds.flag`
- `thresholds.throttle`
- `thresholds.block`
- `runtime.observe_only`
- `ai.mode`

These are still mainly file-backed:

- `runtime.backend`
- `runtime.redis_url`
- `runtime.monitored_window`
- `runtime.monitored_multiplier`
- `ai.model`
- `ai.base_url`
- `ai.api_key`
- `ai.timeout_secs`
- `meta.strictness`

So "saved" and "live right now" are related, but not identical.

## A practical Redis setup

1. install the Redis extra
2. run a Redis-compatible server
3. point one Adiuvare runtime at it
4. keep `meta.instances: single` unless you are deliberately experimenting

```bash
pip install "adiuvare[redis]"
```

```yaml
runtime:
  backend: redis
  redis_url: redis://127.0.0.1:6379/0

meta:
  instances: single
```

```bash
adv status
```

```text
config: H:\ADIUVARE\adiuvare.yaml
runtime: connected
backend: redis
framework: fastapi
instances: single
observe_only: False
ai_mode: off
recent_events: 2
```

## A practical AI setup

1. run an Ollama-compatible endpoint
2. make sure the model you want exists there
3. set `ai.model`, `ai.base_url`, and `ai.timeout_secs`
4. enable AI on the routes where it matters first

```bash
ollama pull llama3
```

```yaml
ai:
  enabled: true
  mode: assist
  model: llama3
  base_url: http://127.0.0.1:11434
```

```python
@app.post("/review")
@guard.protect(ai_mode="critical", sensitivity="critical")
async def review():
    return {"ok": True}
```

## Related

- [Installation](installation.md)
- [Quickstart](quickstart.md)
- [AI](ai.md)
- [Runtime stream](operator/runtime-stream.md)
- [Config API](api/config.md)
