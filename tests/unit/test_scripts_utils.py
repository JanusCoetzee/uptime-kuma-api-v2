import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[2] / "scripts"


@pytest.fixture
def utils(monkeypatch):
    spec = importlib.util.spec_from_file_location("scripts_utils", SCRIPTS / "utils.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_require_titles_passes_when_all_present(utils):
    utils.require_titles("things", ["a"], {"a": "A"}, "s.py")


def test_require_titles_names_every_missing_item(utils):
    with pytest.raises(SystemExit, match="b, c"):
        utils.require_titles("things", ["a", "b", "c"], {"a": "A"}, "s.py")


@pytest.fixture
def template(utils, tmp_path, monkeypatch):
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    (scripts / "t.j2").write_text("value={{ v }}\n")
    monkeypatch.setattr(utils, "SCRIPTS_DIR", scripts)
    monkeypatch.setattr(utils, "REPO_ROOT", tmp_path)
    return tmp_path / "out.txt"


def test_write_to_file_writes(utils, template, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["x"])
    utils.write_to_file("t.j2", "out.txt", v=1)
    assert template.read_text() == "value=1\n"


def test_check_passes_without_writing_when_current(utils, template, monkeypatch):
    template.write_text("value=1\n")
    monkeypatch.setattr(sys, "argv", ["x", "--check"])
    utils.write_to_file("t.j2", "out.txt", v=1)
    assert template.read_text() == "value=1\n"


def test_check_fails_with_diff_and_keeps_file_when_stale(utils, template, monkeypatch, capsys):
    template.write_text("value=old\n")
    monkeypatch.setattr(sys, "argv", ["x", "--check"])
    with pytest.raises(SystemExit, match="out of date"):
        utils.write_to_file("t.j2", "out.txt", v=2)
    assert "-value=old" in capsys.readouterr().out
    assert template.read_text() == "value=old\n"


def test_unknown_flag_is_rejected_not_treated_as_write(utils, template, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["x", "--chek"])
    with pytest.raises(SystemExit, match="unknown option"):
        utils.write_to_file("t.j2", "out.txt", v=1)
    assert not template.exists()
