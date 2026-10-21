import importlib.util
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def case_module():
    spec = importlib.util.spec_from_file_location(
        "uptime_kuma_test_case", TESTS / "uptime_kuma_test_case.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("url", [
    "http://127.0.0.1:3001",
    "http://localhost:3001",
    "http://[::1]:3001",
    "http://127.5.5.5",
])
def test_loopback_urls_are_allowed(case_module, url):
    case_module.check_safe_target(url, environ={})


@pytest.mark.parametrize("url", [
    "http://kuma.example.com:3001",
    "https://192.168.1.10",
    "http://localhost.example.com",
    "http://kuma.indlovu.local:3001",
])
def test_remote_urls_are_refused_without_the_override(case_module, url):
    with pytest.raises(RuntimeError, match="refusing to run"):
        case_module.check_safe_target(url, environ={})


@pytest.mark.parametrize("value", ["", "0", "true", "yes"])
def test_only_exactly_1_allows_remote(case_module, value):
    with pytest.raises(RuntimeError):
        case_module.check_safe_target(
            "http://kuma.example.com",
            environ={"UPTIME_KUMA_TEST_ALLOW_REMOTE": value})


def test_override_allows_remote(case_module):
    case_module.check_safe_target(
        "http://kuma.example.com",
        environ={"UPTIME_KUMA_TEST_ALLOW_REMOTE": "1"})


def test_a_remote_url_aborts_before_anything_connects(
        case_module, monkeypatch):
    monkeypatch.setattr(
        case_module.UptimeKumaTestCase, "url", "http://kuma.example.com")
    monkeypatch.delenv("UPTIME_KUMA_TEST_ALLOW_REMOTE", raising=False)
    with pytest.raises(RuntimeError, match="refusing to run"):
        case_module.UptimeKumaTestCase.setUpClass()


def test_the_guard_runs_before_any_client_is_built(case_module, monkeypatch):
    monkeypatch.setattr(
        case_module.UptimeKumaTestCase, "url", "http://kuma.example.com")
    monkeypatch.delenv("UPTIME_KUMA_TEST_ALLOW_REMOTE", raising=False)
    built = []
    monkeypatch.setattr(
        case_module, "UptimeKumaApi", lambda *a, **k: built.append(a))
    with pytest.raises(RuntimeError):
        case_module.UptimeKumaTestCase.setUpClass()
    assert built == []


def test_the_override_is_read_from_the_environment(case_module, monkeypatch):
    monkeypatch.setattr(
        case_module.UptimeKumaTestCase, "url", "http://kuma.example.com")
    monkeypatch.setenv("UPTIME_KUMA_TEST_ALLOW_REMOTE", "1")
    case_module.UptimeKumaTestCase.setUpClass()


def test_the_url_comes_from_uptime_kuma_url(monkeypatch):
    monkeypatch.setenv("UPTIME_KUMA_URL", "http://kuma.example.com:3001")
    spec = importlib.util.spec_from_file_location(
        "uptime_kuma_test_case_env", TESTS / "uptime_kuma_test_case.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module.UptimeKumaTestCase.url == "http://kuma.example.com:3001"
