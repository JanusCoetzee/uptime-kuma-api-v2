"""Monitors, notifications and status pages against the fake client."""
import json
from unittest import mock

import pytest
import requests

from tests.unit.fake_kuma import make_api
from uptime_kuma_api import (
    AuthMethod,
    Event,
    IncidentStyle,
    MonitorStatus,
    MonitorType,
    NotificationType,
    Timeout,
    UptimeKumaException,
)


class Base:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.api = make_api()
        self.sio = self.api.sio
        self.data = self.api._event_data


def raw_monitor(**overrides):
    monitor = {"id": 1, "name": "m", "type": "http", "active": 1,
               "authMethod": None, "notificationIDList": {"3": True},
               "interval": 60, "retryInterval": 60, "maxretries": 1,
               "url": "http://x", "maxredirects": 10,
               "accepted_statuscodes": ["200-299"],
               "dns_resolve_type": "A"}
    monitor.update(overrides)
    return monitor


class TestMonitors(Base):
    def test_get_monitors_converts_the_cache(self):
        self.data[Event.MONITOR_LIST] = {"1": raw_monitor()}
        (monitor,) = self.api.get_monitors()
        assert monitor["notificationIDList"] == [3]
        # the cache itself keeps the raw form
        assert self.data[Event.MONITOR_LIST]["1"]["notificationIDList"] == {"3": True}

    def test_get_monitor_converts_the_reply(self):
        self.sio.replies["getMonitor"] = {"ok": True, "monitor": raw_monitor()}
        monitor = self.api.get_monitor(1)
        assert monitor["active"] is True
        assert monitor["type"] == MonitorType.HTTP
        assert monitor["authMethod"] == AuthMethod.NONE
        assert monitor["notificationIDList"] == [3]

    def test_add_http_monitor_payload(self):
        self.api.add_monitor(type=MonitorType.HTTP, name="n",
                             url="http://x", notificationIDList=[5])
        (data,) = self.sio.sent("add")
        assert data["notificationIDList"] == {5: True}
        assert data["accepted_statuscodes"] == ["200-299"]
        assert data["url"] == "http://x"
        assert data["parent"] is None
        assert "timeout" in data

    def test_add_requires_the_type_specific_arguments(self):
        with pytest.raises(TypeError):
            self.api.add_monitor(type=MonitorType.HTTP, name="n")

    def test_push_monitor_gets_a_token(self):
        self.api.add_monitor(type=MonitorType.PUSH, name="n")
        (data,) = self.sio.sent("add")
        assert len(data["pushToken"]) == 32

    def test_keyword_monitor_fields(self):
        self.api.add_monitor(type=MonitorType.KEYWORD, name="n",
                             url="http://x", keyword="k", invertKeyword=True)
        (data,) = self.sio.sent("add")
        assert (data["keyword"], data["invertKeyword"]) == ("k", True)

    def test_auth_method_fields(self):
        self.api.add_monitor(type=MonitorType.HTTP, name="n", url="u",
                             authMethod=AuthMethod.NTLM,
                             basic_auth_user="u", basic_auth_pass="p",
                             authDomain="d", authWorkstation="w")
        self.api.add_monitor(type=MonitorType.HTTP, name="n", url="u",
                             authMethod=AuthMethod.MTLS, tlsCert="c",
                             tlsKey="k", tlsCa="a")
        self.api.add_monitor(type=MonitorType.HTTP, name="n", url="u",
                             authMethod=AuthMethod.OAUTH2_CC,
                             oauth_auth_method="client_secret_basic",
                             oauth_token_url="t", oauth_client_id="i",
                             oauth_client_secret="s", oauth_scopes="x")
        ntlm, mtls, oauth = self.sio.sent("add")
        assert (ntlm["authDomain"], ntlm["basic_auth_user"]) == ("d", "u")
        assert mtls["tlsKey"] == "k"
        assert oauth["oauth_token_url"] == "t"

    def test_default_ports(self):
        self.api.add_monitor(type=MonitorType.DNS, name="n", hostname="h",
                             dns_resolve_server="1.1.1.1")
        self.api.add_monitor(type=MonitorType.RADIUS, name="n", hostname="h",
                             radiusUsername="u", radiusPassword="p",
                             radiusSecret="s", radiusCalledStationId="c",
                             radiusCallingStationId="d")
        dns, radius = self.sio.sent("add")
        assert (dns["port"], radius["port"]) == (53, 1812)
        assert radius["radiusSecret"] == "s"

    def test_database_and_docker_fields(self):
        self.api.add_monitor(type=MonitorType.POSTGRES, name="n",
                             databaseConnectionString="postgres://",
                             databaseQuery="select 1")
        self.api.add_monitor(type=MonitorType.DOCKER, name="n",
                             docker_container="c", docker_host=1)
        pg, docker = self.sio.sent("add")
        assert pg["databaseQuery"] == "select 1"
        assert docker["docker_container"] == "c"

    def test_json_query_gamedig_and_grpc_fields(self):
        self.api.add_monitor(type=MonitorType.JSON_QUERY, name="n", url="u",
                             jsonPath="$.a", expectedValue="1")
        self.api.add_monitor(type=MonitorType.GAMEDIG, name="n", game="g",
                             hostname="h", port=1,
                             gamedigGivenPortOnly=False)
        self.api.add_monitor(type=MonitorType.GRPC_KEYWORD, name="n",
                             grpcUrl="g", grpcServiceName="s",
                             grpcMethod="m", keyword="k", url="u")
        jq, game, grpc = self.sio.sent("add")
        assert jq["jsonPath"] == "$.a"
        assert game["gamedigGivenPortOnly"] is False
        assert grpc["grpcUrl"] == "g"

    def test_kafka_defaults(self):
        self.api.add_monitor(type=MonitorType.KAFKA_PRODUCER, name="n",
                             kafkaProducerTopic="t",
                             kafkaProducerMessage="m")
        (data,) = self.sio.sent("add")
        assert data["kafkaProducerBrokers"] == []
        assert data["kafkaProducerSaslOptions"] == {"mechanism": "None"}

    def test_edit_merges_into_the_current_monitor(self):
        self.sio.replies["getMonitor"] = {"ok": True, "monitor": raw_monitor()}
        self.api.edit_monitor(1, name="renamed")
        (data,) = self.sio.sent("editMonitor")
        assert data["name"] == "renamed"
        assert data["notificationIDList"] == {3: True}

    def test_invalid_values_are_rejected_before_sending(self):
        with pytest.raises(ValueError, match="accepted_statuscodes"):
            self.api.add_monitor(type=MonitorType.HTTP, name="n", url="u",
                                 accepted_statuscodes=["1000"])
        with pytest.raises(ValueError, match="dns_resolve_type"):
            self.api.add_monitor(type=MonitorType.DNS, name="n",
                                 hostname="h", dns_resolve_server="1.1.1.1",
                                 dns_resolve_type="BOGUS")
        assert self.sio.calls == []

    def test_delete(self):
        self.data[Event.MONITOR_LIST] = {"1": raw_monitor()}
        self.api.delete_monitor(1)
        assert self.sio.sent("deleteMonitor") == [1]
        with pytest.raises(UptimeKumaException):
            self.api.delete_monitor(2)

    def test_monitor_status_is_the_latest_heartbeat(self):
        self.data[Event.HEARTBEAT_LIST] = {
            1: [{"status": 0, "important": 0}, {"status": 2, "important": 0}]}
        assert self.api.get_monitor_status(1) == MonitorStatus.PENDING


class TestNotifications(Base):
    @pytest.fixture(autouse=True)
    def _setup_more(self, _setup):
        self.data[Event.NOTIFICATION_LIST] = [{
            "id": 1, "name": "n", "isDefault": 0, "userId": 1,
            "config": json.dumps({
                "name": "n", "type": "PushByTechulus", "pushAPIKey": "k"}),
        }]

    def test_get_merges_the_config(self):
        (notification,) = self.api.get_notifications()
        assert notification["pushAPIKey"] == "k"
        assert notification["type"] == NotificationType.PUSHBYTECHULUS
        assert "config" not in notification
        assert self.api.get_notification(1)["id"] == 1
        with pytest.raises(UptimeKumaException):
            self.api.get_notification(2)

    def test_add_and_test(self):
        kwargs = dict(name="n", type=NotificationType.PUSHBYTECHULUS,
                      pushAPIKey="k")
        self.api.add_notification(**kwargs)
        self.api.test_notification(**kwargs)
        data, id_ = self.sio.sent("addNotification")[0]
        assert (data["pushAPIKey"], id_) == ("k", None)
        assert self.sio.sent("testNotification")[0]["name"] == "n"

    def test_add_rejects_unknown_and_missing_options(self):
        with pytest.raises(TypeError, match="unknown argument"):
            self.api.add_notification(
                name="n", type=NotificationType.PUSHBYTECHULUS,
                pushAPIKey="k", bogus=1)
        with pytest.raises(TypeError):
            self.api.add_notification(
                name="n", type=NotificationType.PUSHBYTECHULUS)

    def test_edit_keeps_the_options_of_the_same_type(self):
        self.api.edit_notification(1, name="renamed")
        data, id_ = self.sio.sent("addNotification")[0]
        assert (data["name"], data["pushAPIKey"], id_) == ("renamed", "k", 1)

    def test_edit_to_another_type_drops_the_old_options(self):
        self.api.edit_notification(
            1, type=NotificationType.WEBHOOK, webhookURL="http://h",
            webhookContentType="json")
        data, _ = self.sio.sent("addNotification")[0]
        assert "pushAPIKey" not in data
        assert data["webhookURL"] == "http://h"

    def test_delete(self):
        self.api.delete_notification(1)
        assert self.sio.sent("deleteNotification") == [1]
        with pytest.raises(UptimeKumaException):
            self.api.delete_notification(2)


def http_reply(payload=None, error=None):
    response = mock.Mock()
    if isinstance(error, Exception):
        return mock.Mock(side_effect=error)
    response.json.return_value = payload
    return mock.Mock(return_value=response)


class TestStatusPages(Base):
    GET = "uptime_kuma_api._mixins.status_pages.requests.get"

    @pytest.fixture(autouse=True)
    def _setup_more(self, _setup):
        self.sio.replies["getStatusPage"] = {
            "ok": True, "config": {"id": 5, "slug": "s", "title": "t"}}
        self.page = {
            "config": {"icon": "/i.svg"},
            "incident": {"id": 1, "style": "danger"},
            "publicGroupList": [{"name": "g", "monitorList": [
                {"id": 1, "sendUrl": 1}]}],
            "maintenanceList": [],
        }

    def test_get_status_pages(self):
        self.data[Event.STATUS_PAGE_LIST] = {"5": {"id": 5, "slug": "s"}}
        assert self.api.get_status_pages() == [{"id": 5, "slug": "s"}]

    def test_get_status_page_combines_both_sources(self):
        with mock.patch(self.GET, http_reply(self.page)) as get:
            page = self.api.get_status_page("a/b")
        assert "a%2Fb" in get.call_args.args[0]
        assert page["icon"] == "/i.svg"
        assert page["incident"]["style"] == IncidentStyle.DANGER
        assert len(page["incidents"]) == 1
        assert page["publicGroupList"][0]["monitorList"][0]["sendUrl"] is True

    def test_get_status_page_without_incident(self):
        self.page.pop("incident")
        with mock.patch(self.GET, http_reply(self.page)):
            page = self.api.get_status_page("s")
        assert page["incident"] is None
        assert page["incidents"] == []

    @pytest.mark.parametrize("error, expected", [
        (requests.exceptions.Timeout("t"), Timeout),
        (requests.exceptions.ConnectionError("c"), UptimeKumaException),
        (ValueError("not json"), UptimeKumaException),
    ], ids=["timeout", "connection", "invalid-json"])
    def test_http_errors_are_mapped(self, error, expected):
        with mock.patch(self.GET, http_reply(error=error)):
            with pytest.raises(expected):
                self.api.get_status_page("s")

    def test_add_and_delete(self):
        self.data[Event.STATUS_PAGE_LIST] = {"5": {"id": 5, "slug": "s"}}
        self.api.add_status_page("new", "New")
        assert self.sio.sent("addStatusPage") == [("New", "new")]
        self.api.delete_status_page("s")
        assert self.sio.sent("deleteStatusPage") == ["s"]
        assert self.data[Event.STATUS_PAGE_LIST] == {}
        with pytest.raises(UptimeKumaException):
            self.api.delete_status_page("s")

    def test_save_round_trips_the_page_and_updates_the_cache(self):
        with mock.patch(self.GET, http_reply(self.page)):
            self.api.save_status_page("s", title="new")
            self.api.save_status_page(
                "s", publicGroupList=[{"name": "other", "monitorList": []}])
        first, second = self.sio.sent("saveStatusPage")
        assert first[1]["title"] == "new"
        assert first[3][0]["name"] == "g"
        assert second[3][0]["name"] == "other"
        assert "incident" not in first[1]
        assert self.data[Event.STATUS_PAGE_LIST]["5"]["id"] == 5

    def test_post_and_unpin_incident(self):
        self.sio.replies["postIncident"] = {
            "ok": True, "incident": {"id": 1, "style": "info"}}
        with mock.patch(self.GET, http_reply(self.page)):
            incident = self.api.post_incident("s", "t", "c",
                                              IncidentStyle.INFO)
            self.api.unpin_incident("s")
        assert incident["style"] == IncidentStyle.INFO
        assert self.sio.sent("postIncident")[0][1]["title"] == "t"
        assert self.sio.sent("unpinIncident") == ["s"]
        assert len(self.sio.sent("saveStatusPage")) == 2

    def test_build_status_page_data(self):
        slug, config, icon, groups = self.api._build_status_page_data(
            "s", id=1, title="t")
        assert (slug, config["theme"], icon, groups) == ("s", "auto", "/icon.svg", [])
        assert "showCertificateExpiry" in config
        with pytest.raises(ValueError):
            self.api._build_status_page_data("s", id=1, title="t",
                                             theme="neon")

    def test_old_servers_default_to_the_light_theme(self):
        self.data[Event.INFO] = {"version": "1.21.0"}
        self.api._version = None
        _, config, _, _ = self.api._build_status_page_data(
            "s", id=1, title="t")
        assert config["theme"] == "light"
        assert "showCertificateExpiry" not in config
