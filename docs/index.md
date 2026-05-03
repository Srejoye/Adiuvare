# Adiuvare Docs

Adiuvare is an in-process security layer for Python APIs. It sits inside your
app, scores requests early, and gives you a small operator surface while the
app is running.

If you are starting from zero, go in this order:

1. [Installation](installation.md)
2. [Quickstart](quickstart.md)
3. [Configuration](configuration.md)

## Framework guides

Pick the page that matches your app:

- [FastAPI](integrations/fastapi.md)
- [Flask](integrations/flask.md)
- [Django](integrations/django.md)
- [SQLAlchemy sink hooks](integrations/sqlalchemy.md)

If you are undecided, start with FastAPI. It is still the clearest first
example of the intended request path.

## Operator guides

These are the pages you will use once the app is live:

- [CLI](operator/cli.md)
- [TUI](operator/tui.md)
- [Runtime stream](operator/runtime-stream.md)

In practice:

- use the CLI for quick checks and small actions
- use the TUI for the fuller live console
- use the runtime-stream page when you want to understand how those tools talk
  to the running app

## Extension guides

Use these when the default behavior is close, but not quite enough:

- [Built-in signals](signals.md)
- [Custom signals](extending/custom-signals.md)
- [Route policies](extending/route-policies.md)

That is the main extension story today:

- understand where scores come from
- add your own signals when needed
- change posture per route

## AI

- [AI integration](ai.md)

This is the guide for request-time AI review and the TUI Analyze and Ask
screens.

## API reference

These pages mark the public API boundary:

- [API overview](api/overview.md)
- [Guard](api/guard.md)
- [Config models and loader](api/config.md)
- [Signals and base classes](api/signals.md)
- [Core models](api/models.md)

## Read before release use

- [Limitations](limitations.md)

That page is the honest answer to "what is strong already?" and "where is the
boundary still narrower than a larger platform product?"
