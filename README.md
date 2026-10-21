# uptime-kuma-client

[![CI](https://github.com/JanusCoetzee/uptime-kuma-client/actions/workflows/ci.yml/badge.svg)](https://github.com/JanusCoetzee/uptime-kuma-client/actions/workflows/ci.yml)

A Python wrapper for the [Uptime Kuma](https://github.com/louislam/uptime-kuma) Socket.IO API: manage monitors, notifications, proxies, status pages, maintenance windows, API keys and more from code.

The code examples, the version numbers, the links, the security behaviour and the development commands in this README are checked by the unit tests (`tests/unit/test_readme.py`): the code blocks marked `tested` are run against an offline fake server, and the rest is compared with the repository. The statements about PyPI and Read the Docs are facts about other services and are not tested.

## What it is

- A client for **Uptime Kuma 2.x** (1.x is not supported). Requires Python 3.12+.
- Arguments are validated before anything is sent: an unknown argument to the `add_*` and `edit_*` methods (and `save_status_page`), or a missing one to `add_*`, raises `TypeError`, an invalid value raises `ValueError`. Errors from the server or the connection raise `UptimeKumaException` or a subclass.
- It is derived from [lucasheld/uptime-kuma-api](https://github.com/lucasheld/uptime-kuma-api) but is maintained independently: the library has its own version number and follows Uptime Kuma 2.5, and the argument validation and exception contract above are part of its documented behaviour. Expect API changes between major versions only (see [CHANGELOG.md](CHANGELOG.md)).

## Supported Uptime Kuma versions

<!-- tested: versions -->

| Uptime Kuma | uptime-kuma-client |
|-------------|--------------------|
| 2.5.6 | 2.0.0 (tested in CI) |

Releases 1.0.x of the earlier exaland fork (Uptime Kuma 2.0.0-beta.2) are a different project and are not covered here. The library has its own version, independent of the Uptime Kuma version, and follows [semantic versioning](https://semver.org/) from 2.0.0. The integration tests run against Uptime Kuma 2.5.6, built from source in CI. Other 2.x versions are expected to work but are not tested. Uptime Kuma 3.0 is not supported.

## Install

This project is not on PyPI yet (checked 2026-10-21), and the name `uptime-kuma-client` is not registered, so install from GitHub rather than from an index:

```
pip install git+https://github.com/JanusCoetzee/uptime-kuma-client
```

The import package is `uptime_kuma_client`. Coming from the original library there is no compatibility alias: update your imports (see the breaking change in [CHANGELOG.md](CHANGELOG.md)).

## Example

<!-- tested: quickstart -->

```python
import os

from uptime_kuma_client import MonitorType, UptimeKumaApi

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

from uptime_kuma_client import MonitorType, Timeout, UptimeKumaApi, UptimeKumaException

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

The guide and API reference are in [docs/](docs/); build them with `make -C docs html` (output in `docs/_build/html`).

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

This project is derived from [uptime-kuma-api](https://github.com/lucasheld/uptime-kuma-api) by [Lucas Held](https://github.com/lucasheld) (MIT licensed), via the [exaland/uptime-kuma-api-v2](https://github.com/exaland/uptime-kuma-api-v2) fork that added Uptime Kuma 2.x support. Thank you to both authors. It is now maintained independently and has diverged significantly from both. Both original copyright notices are kept in [LICENSE](LICENSE).
