# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

The history before this file was restarted (releases 1.0.x - 1.2.x and the
upstream project's changes) is not carried over. It remains available:
- in git: `git show 5145ee5:CHANGELOG.md`
- upstream: <https://github.com/lucasheld/uptime-kuma-api/blob/master/CHANGELOG.md>

## [Unreleased]

### Added

- User guide (`docs/guide.rst`): connecting, authentication, exceptions, timing options, compatibility and regeneration notes.

### Changed
- **Breaking:** minimum Python is now 3.12 (3.9 is EOL); CI tests 3.12-3.14.
- **Behaviour change:** `set_settings` now only changes the arguments you
  pass (all defaults are `None`) and keeps every other server setting. It used
  to reset unspecified settings to library defaults, for example
  `keepDataPeriodDays` back to 180. Pass values explicitly if you relied on
  the reset.
- `get_status_page` returns an `incidents` list (Kuma 2.5.x). `incident` is
  kept as the first incident, or `None`.

### Fixed
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
