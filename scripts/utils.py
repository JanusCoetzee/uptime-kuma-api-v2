import difflib
import os
import re
import sys
from pathlib import Path

import jinja2

SCRIPTS_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS_DIR.parent
# Checkout of the Uptime Kuma source to scrape; override with $KUMA_SRC.
KUMA_SRC = Path(os.environ.get("KUMA_SRC", REPO_ROOT / "uptime-kuma"))


def require_titles(kind, found, titles, script):
    """Fail with the list of new items instead of a bare KeyError."""
    missing = [i for i in found if i not in titles]
    if missing:
        raise SystemExit(
            f"{script}: Uptime Kuma has {kind} with no title: "
            f"{', '.join(missing)}. Add them to the 'titles' dict in {script}."
        )


def deduplicate_list(items):
    out = []
    for i in items:
        if i not in out:
            out.append(i)
    return out


def parse_vue_template(path):
    with open(path) as f:
        vue = f.read()
    match = re.search(r'<template>[\s\S]+</template>', vue, re.MULTILINE)
    template = match.group(0)
    return template


def write_to_file(template, destination, **kwargs):
    unknown = [a for a in sys.argv[1:] if a.startswith("-") and a != "--check"]
    if unknown:
        raise SystemExit(f"unknown option {unknown[0]!r}; the only option is --check")
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(SCRIPTS_DIR), keep_trailing_newline=True
    )
    template = env.get_template(template)
    rendered = template.render(**kwargs)
    target = REPO_ROOT / destination
    if "--check" in sys.argv:
        # drift check: compare instead of writing
        if target.read_text() != rendered:
            diff = difflib.unified_diff(
                target.read_text().splitlines(), rendered.splitlines(),
                f"committed {destination}", "regenerated", lineterm="",
            )
            print("\n".join(list(diff)[:80]))
            raise SystemExit(
                f"{destination} is out of date with Uptime Kuma at {KUMA_SRC}; "
                "regenerate it (see scripts/README.md)"
            )
        return
    target.write_text(rendered)


def diff(old, new):
    for i in new:
        if i not in old:
            print("+", i)
    for i in old:
        if i not in new:
            print("-", i)
    print("")


def type_html_to_py(type_):
    if type_ == "number":
        type_ = "int"
    elif type_ == "checkbox":
        type_ = "bool"
    else:
        type_ = "str"
    return type_
