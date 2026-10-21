# Generator scripts

`uptime_kuma_api/monitor_type.py`, `uptime_kuma_api/notification_providers.py`
and the notification options in `uptime_kuma_api/docstrings.py` are generated from the Uptime Kuma source. They were last generated from
**Uptime Kuma 2.5.6** (commit `7ca4a3d`, the ref pinned in
`docker/kuma-test/versions.env`).

## Regenerate

From any directory, with `beautifulsoup4` and `Jinja2` installed
(`pip install -r dev-requirements.txt`):

```sh
set -a; . docker/kuma-test/versions.env; set +a
git init -q uptime-kuma    # gitignored checkout in the repo root
git -C uptime-kuma fetch --depth 1 https://github.com/louislam/uptime-kuma.git "$KUMA_REF"
git -C uptime-kuma checkout FETCH_HEAD

python scripts/build_monitor_types.py
python scripts/build_notifications.py
python scripts/build_notification_docstring.py   # needs the regenerated providers
```

The checkout can live elsewhere: set `KUMA_SRC=/path/to/uptime-kuma`.
Review the diff, run `pytest tests/unit` and commit.

## Drift check

`python scripts/build_monitor_types.py --check` (and the same for
`build_notifications.py` and `build_notification_docstring.py`) regenerate in memory and fail with a diff if the
committed file differs. The `generated` CI job runs both against the pinned ref,
so bumping `KUMA_REF` without regenerating fails CI.

## When a script fails

- *"monitor types with no title"* / *"notification providers with no title"*:
  Kuma added something new. Monitor titles go in `titles` in
  `build_monitor_types.py`; provider titles are scraped from Kuma's
  `NotificationDialog.vue`, with `titles` in `build_notifications.py` as
  overrides.
- *"form inputs no provider reads"* / *"inputs that have no form field"*:
  add the input to `ignored_inputs` in `build_notifications.py` if it is
  internal or legacy, otherwise fix the scraping.
- A new monitor type also needs argument checks and payload fields by hand
  (see `UNSUPPORTED_MONITOR_TYPES` in `_monitor_args.py`).

## Other scripts

`build_inputs.py` and `build_models.py` are manual comparison helpers and are
not part of the drift check.
`mutation_score.py` is the mutation-testing ratchet.
