## What and why

<!-- One or two sentences. Link the issue: "Closes #123". -->

## Checklist

- [ ] Linked issue (`Closes #...`), or explained why there is none
- [ ] Tests added or updated (`pytest tests/unit`); new logic has a test that fails without it
- [ ] `pre-commit run --all-files` passes (PEP 8 / ruff)
- [ ] Coverage did not drop; `fail_under` in `.coveragerc` raised if coverage rose
- [ ] `CHANGELOG.md` updated under `### Unreleased`
- [ ] Behaviour or API change called out in the CHANGELOG (**Changed** / **Removed**)
- [ ] Docstrings and README updated if public behaviour changed
- [ ] Verified against Uptime Kuma 2.5.x (`docker/kuma-test`) if it touches the Socket.IO calls

## Notes for the reviewer

<!-- Risks, follow-ups, anything surprising. Stacked PR? Say which PR this builds on. -->
