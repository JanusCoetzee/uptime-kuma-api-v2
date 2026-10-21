# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`uptime-kuma-api-v2` is a Python wrapper (fork of lucasheld/uptime-kuma-api) for the Uptime Kuma **Socket.IO** API, targeting Uptime Kuma 2.0.0-beta.x. The only runtime deps are `python-socketio[client]` and `requests` (see [pyproject.toml](pyproject.toml)). Docs are Sphinx ([docs/](docs/)), built on Read the Docs.

## Commands

- Install dev deps: `pip install -r requirements.txt -r dev-requirements.txt`
- Unit tests (no server needed, offline): `pytest tests/unit`. They need `python-socketio` and `requests` installed (importing the package pulls them in), plus `Jinja2` for the `scripts/` helper tests. Known bugs are pinned with `@pytest.mark.xfail(strict=True, reason=...)`. Write them pytest-style (plain `assert`, fixtures, `parametrize`, `pytest.raises`, `caplog`); the integration tests outside `unit/` stay `unittest`.
  - Coverage (`fail_under = 90` in `.coveragerc`, only ever raise it; see #57): `pytest tests/unit --cov`. The unit tests use the offline fake client in `tests/unit/fake_kuma.py` (`make_api()`), which records requests and answers from canned replies.
  - Lint (PEP 8 via ruff `E,W,F,B`, config in `pyproject.toml`; per-file ignores there are debt, never add to them): `pre-commit run --all-files`. Install the hooks once with `pre-commit install`. `master` is blocked from direct commits by a hook.
  - Types (mypy, non-strict, config in `pyproject.toml`): `mypy`. A mixin that uses a new `UptimeKumaApi` member must get it declared in [_mixins/_base.py](uptime_kuma_api/_mixins/_base.py); rename or remove it there too, mypy does not flag a stale stub.
  - Architecture (import-linter, contracts in `pyproject.toml`): `lint-imports`. Layers are `api` > `_mixins` > `_monitor_args`/`_monitor_payload` > `_helpers`, and the enum, exception, `docstrings` and `notification_providers` modules import none of them. Import enums from their own module (`from ..event import Event`), never from the package root: `uptime_kuma_api/__init__` imports `api`, so a root import is a cycle the contracts reject.
  - Mutation testing (slow, runs weekly in CI): `mutmut run`, then `mutmut results`; `python scripts/mutation_score.py` fails below the threshold (85%, a ratchet like coverage; 86.2% at #70). `docstrings.py` is excluded as generated text.
- The tests in `tests/` (outside `unit/`) are **integration tests** that need a live Uptime Kuma at `http://127.0.0.1:3001` (admin / secret123, auto-setup by [tests/uptime_kuma_test_case.py](tests/uptime_kuma_test_case.py)). Each `setUp` deletes all monitors and notifications, so `setUpClass` refuses any non-loopback `UPTIME_KUMA_URL` (default `http://127.0.0.1:3001`) unless `UPTIME_KUMA_TEST_ALLOW_REMOTE=1` is set.
  - Start one (built from source at a pinned commit; we do not use upstream images): `set -a; . docker/kuma-test/versions.env; set +a; docker build -t kuma-test:$KUMA_VERSION --build-arg KUMA_REF=$KUMA_REF docker/kuma-test && docker run -d --rm -p 3001:3001 --name kuma-test kuma-test:$KUMA_VERSION` (~1 min build). Only ever point the tests at this throwaway container; they delete all monitors and notifications.
  - CI does not rebuild it every run: `.github/workflows/kuma-image.yml` publishes it to `ghcr.io/<owner>/uptime-kuma-test:<version>-<tree>` (tree = `git rev-parse --short=12 HEAD:docker/kuma-test`) on pushes to master that touch `docker/kuma-test`, and the integration job pulls that tag, falling back to the build above when it is missing.
  - Kuma rate-limits logins: after a full run, restart the container before the next one.
  - All tests: `python -m unittest discover -s tests`
  - Single test: `python -m unittest tests.test_monitor.TestMonitor.<test_name>`
  - [run_tests.sh](run_tests.sh) builds the image if needed (tag keyed on the Dockerfile tree, like CI), starts it, waits for HTTP 200, runs the suite and stops the container.
- Docs: `make -C docs html`

## Architecture

- [uptime_kuma_api/api.py](uptime_kuma_api/api.py) holds the `UptimeKumaApi` core: connection, `_call`, the event cache and `_event_*` handlers. The public methods live in per-domain mixins in [uptime_kuma_api/_mixins/](uptime_kuma_api/_mixins/) (`monitors`, `tags`, `notifications`, `proxies`, `status_pages`, `heartbeats`, `settings`, `auth`, `docker_hosts`, `maintenance`, `api_keys`), which `UptimeKumaApi` inherits. Module-level helpers sit next to the domain that uses them; helpers shared by several domains are in [_helpers.py](uptime_kuma_api/_helpers.py), and the monitor argument checks are in [_monitor_args.py](uptime_kuma_api/_monitor_args.py). Keep every file under ~800 lines. New subpackages under `uptime_kuma_api/` are picked up automatically by `[tool.setuptools.packages.find]` in [pyproject.toml](pyproject.toml).
  - **Two communication patterns**: (1) request/response via `self._call(event, data)` → `sio.call`, which raises `UptimeKumaException` when the reply has `ok: false`; (2) server-pushed state (monitor list, notifications, heartbeats, etc.) cached in `self._event_data[Event.X]` by `_event_*` handlers, read via `_get_event_data`, which polls until the event arrives and then sleeps `wait_events` seconds because there is no "last message" marker. Getters like `get_monitors()` read the cache; they don't call the server.
  - Module-level helpers: `parse_*`/`_convert_*` translate between server payloads and the enums (`MonitorType`, `AuthMethod`, `NotificationType`, ...), `_build_*_data` assemble payloads with defaults, and `_check_arguments_*` validate kwargs per monitor/notification type, raising on missing/invalid params. New monitor or notification fields generally need changes in several of these places.
- [uptime_kuma_api/docstrings.py](uptime_kuma_api/docstrings.py) generates shared `:param` docstrings (`monitor_docstring`, `notification_docstring`, ...) injected into `add_*`/`edit_*` methods through `append_docstring`, so keep param docs there rather than duplicating them.
- Enums live in small modules (`monitor_type.py`, `auth_method.py`, ...), re-exported in [uptime_kuma_api/__init__.py](uptime_kuma_api/__init__.py).
- [notification_providers.py](uptime_kuma_api/notification_providers.py) and parts of `monitor_type.py`/`docstrings.py` are **generated** by [scripts/](scripts/) (`build_*.py`, Jinja templates `*.j2`) by scraping a checkout of the Uptime Kuma source (at `uptime-kuma/` in the repo root, or wherever `KUMA_SRC` points; the scripts run from any directory). Exact steps and the Kuma version used are in [scripts/README.md](scripts/README.md); the `generated` CI job runs each script with `--check` against the pinned ref, so after bumping `docker/kuma-test/versions.env` regenerate. Scripts need `bs4` and Jinja2 from dev-requirements. Prefer regenerating over hand-editing these files, and put one-off manual exceptions in the scripts' ignore tables.

## Conventions

- `README.md` is tested by `tests/unit/test_readme.py`: a python block needs a `<!-- tested: NAME -->` marker and a test, and the version table must match `__version__` and `docker/kuma-test/versions.env`. Update the README and the test together.
- Version lives in [uptime_kuma_api/__version__.py](uptime_kuma_api/__version__.py) (read dynamically by pyproject.toml); update [CHANGELOG.md](CHANGELOG.md) and the supported-versions table in [README.md](README.md) when bumping or adding Uptime Kuma support.
- `env/` (a committed venv) and `build/` (stale build output that differs from source) are tracked in git by mistake. They are not source, so ignore them and never edit them.
