# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

The history before this file was restarted (releases 1.0.x - 1.2.x and the
upstream project's changes) is not carried over. It remains available:
- in git: `git show 5145ee5:CHANGELOG.md`
- upstream: <https://github.com/lucasheld/uptime-kuma-api/blob/master/CHANGELOG.md>

## [Unreleased]

### Added

- Unit tests cover 98% of the package (was 60%) with an offline fake Socket.IO client; `.coveragerc` now fails below 90%.
- Mutation score 86.2% (was 68.0%) from exact-payload tests for monitor, maintenance, proxy, status page and settings requests; the weekly CI job now fails below 85% (`scripts/mutation_score.py`).
- User guide (`docs/guide.rst`): connecting, authentication, exceptions, timing options, compatibility and regeneration notes.

### Changed
- `api.py` is split into per-domain mixins in `uptime_kuma_api/_mixins/`
  (monitors, notifications, status pages, ...) plus `_helpers.py` and
  `_monitor_args.py`. No public change: `UptimeKumaApi` has the same 89 public
  names and behaviour, and `setup.py` now ships the `_mixins` subpackage.
- **Breaking:** minimum Python is now 3.12 (3.9 is EOL); CI tests 3.12-3.14.
- **Behaviour change:** `set_settings` now only changes the arguments you
  pass (all defaults are `None`) and keeps every other server setting. It used
  to reset unspecified settings to library defaults, for example
  `keepDataPeriodDays` back to 180. Pass values explicitly if you relied on
  the reset.
- `get_status_page` returns an `incidents` list (Kuma 2.5.x). `incident` is
  kept as the first incident, or `None`.

### Fixed
- Socket.IO errors no longer escape the library. `_call` raises `Timeout` for a
  Socket.IO timeout and `UptimeKumaException` for other Socket.IO errors (for
  example a closed connection), and `connect` raises the new
  `UptimeKumaConnectionError` (a subclass of `UptimeKumaException`) instead of
  catching everything with a bare `except:`, so `KeyboardInterrupt` is no longer
  swallowed. The original error is kept as `__cause__` (#18). **Behaviour
  change:** code that caught `socketio.exceptions.TimeoutError` around library
  calls must now catch `Timeout` (or `UptimeKumaException`).
- The monitor cache now handles Kuma 2.x `updateMonitorIntoList` and
  `deleteMonitorFromList` events, so `get_monitors`, heartbeats and uptime work
  right after `add_monitor`/`delete_monitor`.
- `get_status_page` now honours `ssl_verify` and the custom `headers`, escapes the slug in the URL, and raises `Timeout`/`UptimeKumaException` for connection, SSL and invalid-JSON errors from the public status page request.
- `get_status_page` no longer drops incidents on Kuma 2.5.x, which renamed the
  `incident` key to `incidents`.
- `login()` without credentials now raises a `Timeout` that says the server probably requires a username and password, instead of a bare "timed out waiting for event autoLogin".
- The heartbeat cache keeps 150 heartbeats per monitor, not 149. The ordering of `get_heartbeats` (oldest first) and `get_important_heartbeats` (newest first) is now documented.
- `add_monitor_tag` and `delete_monitor_tag` no longer fail when the monitor cache is not loaded yet, and caches the raw server response like the other monitor events.
- Unknown enum values from a newer server (for example a new monitor type) are logged once as a warning on the `uptime_kuma_api.api` logger. The returned value is still the raw one.
- The `add_*`/`edit_*` docstrings now list `:raises TypeError:` (missing or unknown arguments) and `:raises ValueError:` (invalid values). The status page theme error names the valid themes.
- Removed a no-op `except: raise` and a commented-out method; `wait_for_event` is annotated `Iterator[None]`; `run_tests.sh` uses a bash shebang and quotes its variables.
- README lists 1.0.3 and Uptime Kuma 2.5.6 (unreleased), and README and the install page warn about the `uptime_kuma_api` import-name conflict with the original distribution.

- `UptimeKumaApi.version` is cached and no longer sleeps `wait_events` on every access, so `add_monitor`, `add_status_page` and `set_settings` are about a second faster.

- **Behaviour change:** database monitors (SQL Server, PostgreSQL, MySQL, MongoDB, Redis) no longer get a placeholder connection string such as `postgres://username:password@host:port/database` saved as real config. `databaseConnectionString` is now required for them and a `TypeError` is raised before any request when it is missing.

- `add_*`/`edit_*` calls for monitors, notifications, proxies, docker hosts and API keys (and enabling/disabling API keys) now wait for the list update the server pushes afterwards, instead of relying on the `wait_events` sleep. A slow server no longer returns a stale list, and a missing update raises `Timeout`.

- Monitor argument checks: an invalid accepted status code is reported by value instead of printing the whole allowed list, an unknown monitor type raises `ValueError: unsupported monitor type` instead of a `KeyError`, and a missing or `None` `kafkaProducerSaslOptions` is treated as mechanism `None` instead of raising.

- The event cache is now guarded by a lock: the socketio background thread updates it while the caller thread reads it, so a read could see a half-applied update (for example 151 heartbeats before the oldest was dropped).

- Heartbeat list events from the server (`heartbeatList`, `importantHeartbeatList`) are merged into the cache instead of nested as a list inside the list, which broke `get_monitor_status` once a monitor already had cached heartbeats (#102). The new beats are placed before the cached ones, as in Kuma's frontend.

- A repeated login no longer duplicates heartbeats in the cache: a re-sent batch replaces the cached copies of the same beats, matched by `time` (live beats have no `id`) (#107).

### Security
- Push monitor tokens are generated with `secrets` and are 32 characters long
  (they used `random` and 10 characters).

### Development
- README lists 1.0.3 and Uptime Kuma 2.5.6 (unreleased), and README and the install page warn about the `uptime_kuma_api` import-name conflict with the original distribution.
- Server-free unit tests (`tests/unit`), PEP 8 linting with ruff, pre-commit
  hooks, a coverage ratchet (target 90%), scheduled mutation testing with
  mutmut, and a CI workflow with SHA-pinned actions.
- PR validation workflow (`pr-validation.yml`): CodeQL, pip-audit, gitleaks, dependency review, package build check, docs build with warnings as errors, actionlint and a check that every action is SHA-pinned; Dependabot for actions, pip and the test image.
- Integration tests run against an Uptime Kuma built from source at a pinned
  commit (`docker/kuma-test`).
