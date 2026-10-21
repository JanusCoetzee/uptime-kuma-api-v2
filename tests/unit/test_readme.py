"""The README cannot rot: its code runs and its facts match the repository.

Code blocks that follow a ``<!-- tested: NAME -->`` marker are executed
against the offline fake client. A python block without a marker, or a
marker without a test here, fails.
"""
import re
import warnings
import tomllib

import socketio
from pathlib import Path
from unittest import mock

import pytest

import uptime_kuma_api
from tests.unit.fake_kuma import FakeSio

ROOT = Path(__file__).resolve().parents[2]
README = (ROOT / "README.md").read_text()
FENCE = r"```(?:python|py|pycon)\r?\n"
MARKER = re.compile(rf"<!-- tested: (\w+) -->\s*{FENCE}(.*?)```", re.S)
BLOCKS = {name: code for name, code in MARKER.findall(README)}


def test_every_python_block_is_tested():
    marked = {code for code in BLOCKS.values()}
    fenced = re.findall(rf"{FENCE}(.*?)```", README, re.S)
    unmarked = [code for code in fenced if code not in marked]
    assert not unmarked, f"python block without a tested marker: {unmarked}"


def run_block(name, monkeypatch, replies):
    monkeypatch.setenv("KUMA_URL", "https://kuma.test")
    monkeypatch.setenv("KUMA_USER", "admin")
    monkeypatch.setenv("KUMA_PASS", "secret")
    sio = FakeSio()
    sio.replies.update(replies)
    init = uptime_kuma_api.UptimeKumaApi.__init__

    def init_and_link(self, *args, **kwargs):
        init(self, *args, **kwargs)
        sio.api = self  # lets the fake push the list update after a change

    with mock.patch("uptime_kuma_api.api.socketio.Client", return_value=sio):
        with mock.patch.object(
                uptime_kuma_api.UptimeKumaApi, "__init__", init_and_link):
            exec(compile(BLOCKS[name], f"README:{name}", "exec"), {})
    return sio


def test_quickstart_logs_in_adds_a_monitor_and_disconnects(
        monkeypatch, capsys):
    sio = run_block("quickstart", monkeypatch, {
        "login": {"ok": True, "token": "t"},
        "add": {"ok": True, "msg": "Added Successfully.", "monitorID": 1},
    })
    assert sio.sent("login")[0]["username"] == "admin"
    monitor = sio.sent("add")[0]
    assert monitor["name"] == "Example"
    assert monitor["url"] == "https://example.com"
    assert capsys.readouterr().out == "Added Successfully.\n"
    assert sio.connected is False


def test_errors_example_reports_a_timeout_separately(monkeypatch, capsys):
    run_block("errors", monkeypatch, {
        "login": {"ok": True, "token": "t"},
        "getMonitor": socketio.exceptions.TimeoutError(),
    })
    out = capsys.readouterr().out.splitlines()
    assert out[1] == "no answer from the server"


def test_errors_example_prints_both_failures(monkeypatch, capsys):
    run_block("errors", monkeypatch, {
        "login": {"ok": True, "token": "t"},
        "getMonitor": {"ok": False, "msg": "no such monitor"},
    })
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("missing argument:")
    assert "hostname" in out[0]
    assert out[1] == "server error: no such monitor"


def kuma_version():
    env = dict(
        line.split("=") for line in
        (ROOT / "docker/kuma-test/versions.env").read_text().split())
    return env["KUMA_VERSION"]


def test_version_table_matches_the_repository():
    rows = re.findall(r"^\| ([\w.-]+) \| (.+?) \|$", README, re.M)
    assert (kuma_version(), f"{uptime_kuma_api.__version__} (tested in CI)") \
        in rows


def test_kuma_version_prose_matches_the_repository():
    version = kuma_version()
    assert f"run against Uptime Kuma {version}, built from source" in README
    assert "follows Uptime Kuma " + ".".join(version.split(".")[:2]) in README


def test_development_commands_exist():
    pyproject = (ROOT / "pyproject.toml").read_text()
    dev = (ROOT / "dev-requirements.txt").read_text()
    assert "[tool.importlinter]" in pyproject and "lint-imports" in README
    assert "[tool.mypy]" in pyproject and "\nmypy " in README
    assert "mutmut" in dev and "mutmut run" in README
    assert "pre-commit" in dev and "pre-commit install" in README
    gate = re.search(r"fail_under = (\d+)", (ROOT / ".coveragerc").read_text())
    assert f"coverage gate {gate.group(1)}%" in README
    for name in ("run_tests.sh", "docker/kuma-test"):
        assert (ROOT / name).exists() and name.split("/")[-1] in README


def test_python_version_matches_pyproject():
    requires = tomllib.loads(
        (ROOT / "pyproject.toml").read_text())["project"]["requires-python"]
    assert requires.startswith(">=3.12")
    assert "Python 3.12+" in README


LINKS = sorted(set(re.findall(r"\]\(((?!https?:|#)[^)\s]+)\)", README)))


@pytest.mark.parametrize("path", LINKS)
def test_local_links_exist(path):
    assert (ROOT / path).exists()


def test_exception_contract_in_the_readme():
    for sub in (uptime_kuma_api.Timeout,
                uptime_kuma_api.UptimeKumaConnectionError):
        assert issubclass(sub, uptime_kuma_api.UptimeKumaException)
    assert "Timeout" in README and "UptimeKumaConnectionError" in README


def test_integration_guard_variables_exist():
    case = (ROOT / "tests/uptime_kuma_test_case.py").read_text()
    for name in ("UPTIME_KUMA_URL", "UPTIME_KUMA_TEST_ALLOW_REMOTE"):
        assert name in README and name in case


def test_there_are_local_links_to_check():
    assert LINKS


def test_tested_marker_names_are_known():
    assert set(BLOCKS) == {"quickstart", "errors"}
    assert "<!-- tested: versions -->" in README


@pytest.mark.parametrize("url", [
    "https://kuma.example.com", "wss://kuma.example.com",
    "http://localhost:3001", "http://127.0.0.1:3001", "http://[::1]:3001",
])
def test_encrypted_and_loopback_urls_do_not_warn(url):
    with mock.patch("uptime_kuma_api.api.socketio.Client"):
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            uptime_kuma_api.UptimeKumaApi(url)


@pytest.mark.parametrize("url", [
    "http://kuma.example.com", "ws://kuma.example.com"])
def test_clear_text_remote_urls_warn(url):
    with mock.patch("uptime_kuma_api.api.socketio.Client"):
        with pytest.warns(UserWarning, match="not encrypted"):
            uptime_kuma_api.UptimeKumaApi(url)


def test_certificates_are_verified_unless_turned_off():
    with mock.patch("uptime_kuma_api.api.socketio.Client") as client:
        uptime_kuma_api.UptimeKumaApi("https://kuma.test")
        assert client.call_args.kwargs["ssl_verify"] is True
        uptime_kuma_api.UptimeKumaApi("https://kuma.test", ssl_verify=False)
        assert client.call_args.kwargs["ssl_verify"] is False


@pytest.mark.parametrize("args", [("admin", None), (None, "secret")])
def test_login_needs_both_credentials_or_neither(args):
    with mock.patch("uptime_kuma_api.api.socketio.Client"):
        api = uptime_kuma_api.UptimeKumaApi("https://kuma.test")
    with pytest.raises(ValueError, match="together"):
        api.login(*args)
