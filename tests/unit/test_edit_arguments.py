"""``edit_*`` rejects the keyword arguments that ``add_*`` would reject (#140).

An edit merges its keyword arguments into the object the server returned, so
a typo used to be sent to the server (or silently ignored). The accepted names
are the parameters of the ``add_*`` builder plus the fields of that object.
"""
import contextlib
import inspect

import pytest

from tests.unit.fake_kuma import make_api
from uptime_kuma_client import (
    AuthMethod,
    DockerType,
    MaintenanceStrategy,
    MonitorType,
    NotificationType,
    ProxyProtocol,
)
from uptime_kuma_client._helpers import _check_edit_arguments
from uptime_kuma_client._mixins.docker_hosts import _build_docker_host_data
from uptime_kuma_client._mixins.maintenance import MaintenanceMixin
from uptime_kuma_client._mixins.notifications import _build_notification_data
from uptime_kuma_client._mixins.proxies import _build_proxy_data
from uptime_kuma_client._mixins.tags import _build_tag_data
from uptime_kuma_client._monitor_payload import _build_monitor_data

MONITOR = dict(
    id=1, type=MonitorType.HTTP, name="m", interval=60, retryInterval=60,
    maxretries=0, url="http://x", maxredirects=10,
    accepted_statuscodes=["200-299"], dns_resolve_type="A",
    notificationIDList=[1, 2], databaseConnectionString=None,
    authMethod=AuthMethod.NONE, pushToken=None, path=["m"], pathName="m",
    kafkaProducerSaslOptions={"mechanism": "None"},
)
PROXY = dict(
    id=1, protocol=ProxyProtocol.HTTP, host="h", port=80, auth=False,
    username=None, password=None, active=True, default=False,
    applyExisting=False, userId=1, createdDate="2026-01-01 00:00:00")
TAG = dict(id=1, name="t", color="#fff")
DOCKER_HOST = dict(
    id=1, name="d", dockerType=DockerType.SOCKET,
    dockerDaemon="/var/run/docker.sock", userId=1)
MAINTENANCE = dict(
    id=1, title="t", strategy=MaintenanceStrategy.MANUAL, active=True,
    description="", status="under-maintenance")
NOTIFICATION = dict(
    id=1, name="n", type=NotificationType.PUSHBYTECHULUS, isDefault=False,
    applyExisting=False, active=True, userId=1, pushAPIKey="k")

CASES = {
    "edit_monitor": ("get_monitor", MONITOR, dict(interval=20)),
    "edit_proxy": ("get_proxy", PROXY, dict(host="new")),
    "edit_tag": ("get_tag", TAG, dict(color="#000")),
    "edit_docker_host": ("get_docker_host", DOCKER_HOST, dict(name="new")),
    "edit_maintenance": ("get_maintenance", MAINTENANCE, dict(title="new")),
    "edit_notification": (
        "get_notification", NOTIFICATION, dict(name="new")),
}


@pytest.fixture(params=sorted(CASES))
def case(request, monkeypatch):
    method = request.param
    getter, stored, good = CASES[method]
    api = make_api()
    sent = []
    monkeypatch.setattr(api, getter, lambda id_: dict(stored))
    monkeypatch.setattr(api, "_call", lambda *a, **k: sent.append(a) or {})
    monkeypatch.setattr(
        api, "wait_for_event", lambda *a, **k: contextlib.nullcontext())
    return getattr(api, method), method, stored, good, sent


def test_unknown_argument_is_rejected_and_nothing_is_sent(case):
    edit, name, _, _, sent = case
    with pytest.raises(TypeError, match=f"{name}.*'intervall'"):
        edit(1, intervall=60)
    assert sent == []


def test_a_typo_next_to_a_valid_argument_still_fails(case):
    edit, _, _, good, sent = case
    with pytest.raises(TypeError, match="'bogus_field'"):
        edit(1, bogus_field=1, **good)
    assert sent == []


def payload(call):
    """The dict sent, whether or not the event also carries an id."""
    data = call[1]
    return data[0] if isinstance(data, tuple) else data


def test_known_argument_is_sent_with_the_stored_fields(case):
    edit, _, stored, good, sent = case
    edit(1, **good)
    assert len(sent) == 1
    data = payload(sent[0])
    assert all(data[key] == value for key, value in good.items())
    assert data["id"] == stored["id"]


def test_fields_returned_by_get_are_accepted(case):
    edit, _, stored, _, sent = case
    edit(1, **stored)
    assert len(sent) == 1
    assert payload(sent[0])["id"] == stored["id"]


BUILDERS = {
    "edit_monitor": _build_monitor_data,
    "edit_proxy": _build_proxy_data,
    "edit_tag": _build_tag_data,
    "edit_docker_host": _build_docker_host_data,
    "edit_maintenance": MaintenanceMixin._build_maintenance_data,
    "edit_notification": _build_notification_data,
}


@pytest.mark.parametrize("method", sorted(BUILDERS))
def test_every_add_parameter_is_accepted_without_a_stored_field(method):
    """The builder branch alone, so it cannot hide behind the stored dict."""
    builder = BUILDERS[method]
    params = [
        name for name, p in inspect.signature(builder).parameters.items()
        if p.kind is not p.VAR_KEYWORD and name != "self"]
    assert params
    _check_edit_arguments(
        method, dict.fromkeys(params), builder, {}, ["extra_ok"])
    with pytest.raises(TypeError):
        _check_edit_arguments(method, {"nope": 1}, builder, {})


@pytest.mark.parametrize("method", sorted(CASES))
def test_the_error_names_the_method(method):
    with pytest.raises(TypeError, match=rf"^{method}\(\) got an unexpected"):
        _check_edit_arguments(method, {"x": 1}, lambda a: None, {})


def test_edit_accepts_what_add_accepts_for_another_type(monkeypatch):
    """Changing the type brings the new type's own arguments."""
    api = make_api()
    sent = []
    monkeypatch.setattr(api, "get_monitor", lambda id_: dict(MONITOR))
    monkeypatch.setattr(api, "_call", lambda *a, **k: sent.append(a) or {})
    monkeypatch.setattr(
        api, "wait_for_event", lambda *a, **k: contextlib.nullcontext())
    api.edit_monitor(1, type=MonitorType.PORT, hostname="h", port=22)
    assert sent[0][1]["port"] == 22


def test_notification_provider_options_are_accepted(monkeypatch):
    api = make_api()
    sent = []
    monkeypatch.setattr(api, "get_notification", lambda i: dict(NOTIFICATION))
    monkeypatch.setattr(api, "_call", lambda *a, **k: sent.append(a) or {})
    monkeypatch.setattr(
        api, "wait_for_event", lambda *a, **k: contextlib.nullcontext())
    api.edit_notification(
        1, type=NotificationType.WEBHOOK, webhookURL="http://h",
        webhookContentType="json")
    assert sent[0][1][0]["webhookURL"] == "http://h"
    with pytest.raises(TypeError, match="'webhookURLL'"):
        api.edit_notification(1, webhookURLL="http://h")


def test_save_status_page_rejects_an_unknown_argument(monkeypatch):
    api = make_api()
    sent = []
    monkeypatch.setattr(
        api, "get_status_page", lambda slug: dict(id=1, title="t"))
    monkeypatch.setattr(api, "_call", lambda *a, **k: sent.append(a) or {})
    with pytest.raises(TypeError, match="save_status_page.*'titel'"):
        api.save_status_page("s", titel="x")
    assert sent == []
