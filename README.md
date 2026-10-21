# uptime-kuma-api-v2

[![CI](https://github.com/JanusCoetzee/uptime-kuma-api-v2/actions/workflows/ci.yml/badge.svg)](https://github.com/JanusCoetzee/uptime-kuma-api-v2/actions/workflows/ci.yml)

A Python wrapper for the [Uptime Kuma](https://github.com/louislam/uptime-kuma) Socket.IO API: manage monitors, notifications, proxies, status pages, maintenance windows, API keys and more from code.

The code examples, the version numbers, the links, the security behaviour and the development commands in this README are checked by the unit tests (`tests/unit/test_readme.py`): the code blocks marked `tested` are run against an offline fake server, and the rest is compared with the repository. The PyPI and Read the Docs statements are facts about other services, dated below, and are not tested.

## What it is

- A client for **Uptime Kuma 2.x** (1.x is not supported). Requires Python 3.12+.
- Arguments are validated before anything is sent: a missing or unknown argument to the `add_*` methods raises `TypeError`, an invalid value raises `ValueError`. Errors from the server or the connection raise `UptimeKumaException` or a subclass.
- It is a fork of [lucasheld/uptime-kuma-api](https://github.com/lucasheld/uptime-kuma-api) and has diverged from it: the library has its own version number and follows Uptime Kuma 2.5, and the argument validation and exception contract above are part of its documented behaviour. Expect API changes between major versions only (see [CHANGELOG.md](CHANGELOG.md)).

## Supported Uptime Kuma versions

<!-- tested: versions -->

| Uptime Kuma | uptime-kuma-api-v2 |
|-------------|--------------------|
| 2.0.0-beta.2 | 1.0.0 - 1.0.3 |
| 2.5.6 | 2.0.0 (tested in CI) |

The library has its own version, independent of the Uptime Kuma version, and follows [semantic versioning](https://semver.org/) from 2.0.0. The integration tests run against Uptime Kuma 2.5.6, built from source in CI. Other 2.x versions are expected to work but are not tested. Uptime Kuma 3.0 is not supported.

## Install

This repository has not published a release to PyPI. As of 2026-10-21 the `uptime-kuma-api-v2` project on PyPI belongs to someone else (it is the older `exaland` fork, version 1.0.3), so `pip install uptime-kuma-api-v2` does **not** give you this code. Install from GitHub:

```
pip install git+https://github.com/JanusCoetzee/uptime-kuma-api-v2
```

> **Import name conflict:** the import package is `uptime_kuma_api`, the same as the original `uptime-kuma-api` distribution and the older forks. If more than one of them is installed they overwrite each other's files, so install only one.

## Example

<!-- tested: quickstart -->

```python
import os

from uptime_kuma_api import MonitorType, UptimeKumaApi

with UptimeKumaApi(os.environ["KUMA_URL"]) as api:
    api.login(os.environ["KUMA_USER"], os.environ["KUMA_PASS"])
    result = api.add_monitor(
        type=MonitorType.HTTP, name="Example", url="https://example.com")
    print(result["msg"])
```

The `with` block disconnects for you, so the program does not block at exit. Without it, call `api.disconnect()` yourself.

## Error handling

<!-- tested: errors -->

```python
import os

from uptime_kuma_api import MonitorType, Timeout, UptimeKumaApi, UptimeKumaException

with UptimeKumaApi(os.environ["KUMA_URL"]) as api:
    api.login(os.environ["KUMA_USER"], os.environ["KUMA_PASS"])
    try:
        api.add_monitor(type=MonitorType.PORT, name="no host or port")
    except TypeError as e:
        print("missing argument:", e)
    try:
        api.get_monitor(999999)
    except Timeout:
        print("no answer from the server")
    except UptimeKumaException as e:
        print("server error:", e)
```

`Timeout` and `UptimeKumaConnectionError` are subclasses of `UptimeKumaException`, so list `Timeout` first if you want to treat it separately.

## Security notes

- Read credentials from the environment or a secret store, as above, not from source code.
- Use an `https://` (or `wss://`) URL. For an `http://` or `ws://` URL whose host is not loopback (`localhost`, `127.0.0.0/8`, `::1`) the client issues a `UserWarning`, because the password and data would travel in clear text.
- Certificates are verified. `ssl_verify=False` turns that off, for servers with a self-signed certificate; prefer fixing the certificate.
- `login(username, password)` needs both values or neither (neither is the auto-login for servers that run with authentication disabled). Passing only one raises `ValueError`.

## Documentation

The guide and API reference are in [docs/](docs/); build them with `make -C docs html` (output in `docs/_build/html`). A hosted copy is not linked here because the Read the Docs project for this repository has not been set up.

## Development

```
pip install -r requirements.txt -r dev-requirements.txt
pre-commit install            # PEP 8 (ruff) and file hygiene hooks
pytest tests/unit --cov       # offline unit tests, coverage gate 90%
mypy                          # types
lint-imports                  # architecture rules
mutmut run                    # mutation tests (slow)
```

The integration tests in `tests/` need a throwaway Uptime Kuma built from source at a pinned commit (`docker/kuma-test`, started by `run_tests.sh`). They delete all monitors and notifications, so they refuse to run against a non-loopback `UPTIME_KUMA_URL` unless `UPTIME_KUMA_TEST_ALLOW_REMOTE=1` is set. [CLAUDE.md](CLAUDE.md) has the full commands and the architecture notes.

See [CHANGELOG.md](CHANGELOG.md) for what changed between versions.

## Acknowledgements

This project is a fork of [uptime-kuma-api](https://github.com/lucasheld/uptime-kuma-api) by [Lucas Held](https://github.com/lucasheld) (MIT licensed), via the [exaland/uptime-kuma-api-v2](https://github.com/exaland/uptime-kuma-api-v2) fork that added Uptime Kuma 2.x support. Thank you to both authors. It is now maintained independently and is diverging significantly from upstream, so expect API changes. Both original copyright notices are kept in [LICENSE](LICENSE).
