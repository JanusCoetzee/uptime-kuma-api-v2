# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`uptime-kuma-api-v2` is a Python wrapper (fork of lucasheld/uptime-kuma-api) for the Uptime Kuma **Socket.IO** API, targeting Uptime Kuma 2.0.0-beta.x. The only runtime deps are `python-socketio[client]` and `packaging` (see [setup.py](setup.py)). Docs are Sphinx ([docs/](docs/)), built on Read the Docs.

## Commands

- Install dev deps: `pip install -r requirements.txt -r dev-requirements.txt`
- Unit tests (no server needed, offline): `python -m unittest discover -s tests/unit -t .`. They need `python-socketio`, `packaging` and `requests` installed (importing the package pulls them in). Known bugs are pinned with `@unittest.expectedFailure`.
- The tests in `tests/` (outside `unit/`) are **integration tests** that need a live Uptime Kuma at `http://127.0.0.1:3001` (admin / secret123, auto-setup by [tests/uptime_kuma_test_case.py](tests/uptime_kuma_test_case.py)). Each `setUp` deletes all monitors and notifications.
  - Start one: `docker run -d --rm -p 3001:3001 --name uptimekuma louislam/uptime-kuma:<version>`
  - All tests: `python -m unittest discover -s tests`
  - Single test: `python -m unittest tests.test_monitor.TestMonitor.<test_name>`
  - [run_tests.sh](run_tests.sh) loops this over several Docker image versions (its version list is still the old 1.x one; it uses bash arrays despite the `sh` shebang).
- Docs: `make -C docs html`

## Architecture

- [uptime_kuma_api/api.py](uptime_kuma_api/api.py) (~4000 lines) holds everything behavior-related: the `UptimeKumaApi` class plus module-level helpers.
  - **Two communication patterns**: (1) request/response via `self._call(event, data)` → `sio.call`, which raises `UptimeKumaException` when the reply has `ok: false`; (2) server-pushed state (monitor list, notifications, heartbeats, etc.) cached in `self._event_data[Event.X]` by `_event_*` handlers, read via `_get_event_data`, which polls until the event arrives and then sleeps `wait_events` seconds because there is no "last message" marker. Getters like `get_monitors()` read the cache; they don't call the server.
  - Module-level helpers: `parse_*`/`_convert_*` translate between server payloads and the enums (`MonitorType`, `AuthMethod`, `NotificationType`, ...), `_build_*_data` assemble payloads with defaults, and `_check_arguments_*` validate kwargs per monitor/notification type, raising on missing/invalid params. New monitor or notification fields generally need changes in several of these places.
- [uptime_kuma_api/docstrings.py](uptime_kuma_api/docstrings.py) generates shared `:param` docstrings (`monitor_docstring`, `notification_docstring`, ...) injected into `add_*`/`edit_*` methods through `append_docstring`, so keep param docs there rather than duplicating them.
- Enums live in small modules (`monitor_type.py`, `auth_method.py`, ...), re-exported in [uptime_kuma_api/__init__.py](uptime_kuma_api/__init__.py).
- [notification_providers.py](uptime_kuma_api/notification_providers.py) and parts of `monitor_type.py`/`docstrings.py` are **generated** by [scripts/](scripts/) (`build_*.py`, Jinja templates `*.j2`) by scraping a checkout of the Uptime Kuma source (scripts expect it at `uptime-kuma/` relative to the cwd, e.g. `build_notifications.py` reads `uptime-kuma/server/notification-providers/` and `src/components/notifications/`). Scripts need `bs4` and Jinja2 from dev-requirements. Prefer regenerating over hand-editing these files, and put one-off manual exceptions in the scripts' ignore tables.

## Conventions

- Version lives in [uptime_kuma_api/__version__.py](uptime_kuma_api/__version__.py) (read by setup.py); update [CHANGELOG.md](CHANGELOG.md) and the supported-versions table in [README.md](README.md) when bumping or adding Uptime Kuma support.
- `env/` (a committed venv) and `build/` (stale build output that differs from source) are tracked in git by mistake. They are not source, so ignore them and never edit them.
