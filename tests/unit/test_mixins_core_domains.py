"""Monitors, notifications and status pages against the fake client."""
import json
import unittest
from unittest import mock

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


class Base(unittest.TestCase):
    def setUp(self):
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
        self.assertEqual(monitor["notificationIDList"], [3])
        # the cache itself keeps the raw form
        self.assertEqual(self.data[Event.MONITOR_LIST]["1"]
                         ["notificationIDList"], {"3": True})

    def test_get_monitor_converts_the_reply(self):
        self.sio.replies["getMonitor"] = {"ok": True, "monitor": raw_monitor()}
        monitor = self.api.get_monitor(1)
        self.assertIs(monitor["active"], True)
        self.assertEqual(monitor["type"], MonitorType.HTTP)
        self.assertEqual(monitor["authMethod"], AuthMethod.NONE)
        self.assertEqual(monitor["notificationIDList"], [3])

    def test_add_http_monitor_payload(self):
        self.api.add_monitor(type=MonitorType.HTTP, name="n",
                             url="http://x", notificationIDList=[5])
        (data,) = self.sio.sent("add")
        self.assertEqual(data["notificationIDList"], {5: True})
        self.assertEqual(data["accepted_statuscodes"], ["200-299"])
        self.assertEqual(data["url"], "http://x")
        self.assertEqual(data["parent"], None)
        self.assertIn("timeout", data)

    def test_add_requires_the_type_specific_arguments(self):
        with self.assertRaises(TypeError):
            self.api.add_monitor(type=MonitorType.HTTP, name="n")

    def test_push_monitor_gets_a_token(self):
        self.api.add_monitor(type=MonitorType.PUSH, name="n")
        (data,) = self.sio.sent("add")
        self.assertEqual(len(data["pushToken"]), 32)

    def test_keyword_monitor_fields(self):
        self.api.add_monitor(type=MonitorType.KEYWORD, name="n",
                             url="http://x", keyword="k", invertKeyword=True)
        (data,) = self.sio.sent("add")
        self.assertEqual((data["keyword"], data["invertKeyword"]),
                         ("k", True))

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
        self.assertEqual((ntlm["authDomain"], ntlm["basic_auth_user"]),
                         ("d", "u"))
        self.assertEqual(mtls["tlsKey"], "k")
        self.assertEqual(oauth["oauth_token_url"], "t")

    def test_default_ports(self):
        self.api.add_monitor(type=MonitorType.DNS, name="n", hostname="h",
                             dns_resolve_server="1.1.1.1")
        self.api.add_monitor(type=MonitorType.RADIUS, name="n", hostname="h",
                             radiusUsername="u", radiusPassword="p",
                             radiusSecret="s", radiusCalledStationId="c",
                             radiusCallingStationId="d")
        dns, radius = self.sio.sent("add")
        self.assertEqual((dns["port"], radius["port"]), (53, 1812))
        self.assertEqual(radius["radiusSecret"], "s")

    def test_database_and_docker_fields(self):
        self.api.add_monitor(type=MonitorType.POSTGRES, name="n",
                             databaseConnectionString="postgres://",
                             databaseQuery="select 1")
        self.api.add_monitor(type=MonitorType.DOCKER, name="n",
                             docker_container="c", docker_host=1)
        pg, docker = self.sio.sent("add")
        self.assertEqual(pg["databaseQuery"], "select 1")
        self.assertEqual(docker["docker_container"], "c")

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
        self.assertEqual(jq["jsonPath"], "$.a")
        self.assertIs(game["gamedigGivenPortOnly"], False)
        self.assertEqual(grpc["grpcUrl"], "g")

    def test_kafka_defaults(self):
        self.api.add_monitor(type=MonitorType.KAFKA_PRODUCER, name="n",
                             kafkaProducerTopic="t",
                             kafkaProducerMessage="m")
        (data,) = self.sio.sent("add")
        self.assertEqual(data["kafkaProducerBrokers"], [])
        self.assertEqual(data["kafkaProducerSaslOptions"],
                         {"mechanism": "None"})

    def test_edit_merges_into_the_current_monitor(self):
        self.sio.replies["getMonitor"] = {"ok": True, "monitor": raw_monitor()}
        self.api.edit_monitor(1, name="renamed")
        (data,) = self.sio.sent("editMonitor")
        self.assertEqual(data["name"], "renamed")
        self.assertEqual(data["notificationIDList"], {3: True})

    def test_invalid_values_are_rejected_before_sending(self):
        with self.assertRaisesRegex(ValueError, "accepted_statuscodes"):
            self.api.add_monitor(type=MonitorType.HTTP, name="n", url="u",
                                 accepted_statuscodes=["1000"])
        with self.assertRaisesRegex(ValueError, "dns_resolve_type"):
            self.api.add_monitor(type=MonitorType.DNS, name="n",
                                 hostname="h", dns_resolve_server="1.1.1.1",
                                 dns_resolve_type="BOGUS")
        self.assertEqual(self.sio.calls, [])

    def test_delete(self):
        self.data[Event.MONITOR_LIST] = {"1": raw_monitor()}
        self.api.delete_monitor(1)
        self.assertEqual(self.sio.sent("deleteMonitor"), [1])
        with self.assertRaises(UptimeKumaException):
            self.api.delete_monitor(2)

    def test_monitor_status_is_the_latest_heartbeat(self):
        self.data[Event.HEARTBEAT_LIST] = {
            1: [{"status": 0, "important": 0}, {"status": 2, "important": 0}]}
        self.assertEqual(self.api.get_monitor_status(1), MonitorStatus.PENDING)


class TestNotifications(Base):
    def setUp(self):
        super().setUp()
        self.data[Event.NOTIFICATION_LIST] = [{
            "id": 1, "name": "n", "isDefault": 0, "userId": 1,
            "config": json.dumps({
                "name": "n", "type": "PushByTechulus", "pushAPIKey": "k"}),
        }]

    def test_get_merges_the_config(self):
        (notification,) = self.api.get_notifications()
        self.assertEqual(notification["pushAPIKey"], "k")
        self.assertEqual(notification["type"],
                         NotificationType.PUSHBYTECHULUS)
        self.assertNotIn("config", notification)
        self.assertEqual(self.api.get_notification(1)["id"], 1)
        with self.assertRaises(UptimeKumaException):
            self.api.get_notification(2)

    def test_add_and_test(self):
        kwargs = dict(name="n", type=NotificationType.PUSHBYTECHULUS,
                      pushAPIKey="k")
        self.api.add_notification(**kwargs)
        self.api.test_notification(**kwargs)
        data, id_ = self.sio.sent("addNotification")[0]
        self.assertEqual((data["pushAPIKey"], id_), ("k", None))
        self.assertEqual(self.sio.sent("testNotification")[0]["name"], "n")

    def test_add_rejects_unknown_and_missing_options(self):
        with self.assertRaisesRegex(TypeError, "unknown argument"):
            self.api.add_notification(
                name="n", type=NotificationType.PUSHBYTECHULUS,
                pushAPIKey="k", bogus=1)
        with self.assertRaises(TypeError):
            self.api.add_notification(
                name="n", type=NotificationType.PUSHBYTECHULUS)

    def test_edit_keeps_the_options_of_the_same_type(self):
        self.api.edit_notification(1, name="renamed")
        data, id_ = self.sio.sent("addNotification")[0]
        self.assertEqual((data["name"], data["pushAPIKey"], id_),
                         ("renamed", "k", 1))

    def test_edit_to_another_type_drops_the_old_options(self):
        self.api.edit_notification(
            1, type=NotificationType.WEBHOOK, webhookURL="http://h",
            webhookContentType="json")
        data, _ = self.sio.sent("addNotification")[0]
        self.assertNotIn("pushAPIKey", data)
        self.assertEqual(data["webhookURL"], "http://h")

    def test_delete(self):
        self.api.delete_notification(1)
        self.assertEqual(self.sio.sent("deleteNotification"), [1])
        with self.assertRaises(UptimeKumaException):
            self.api.delete_notification(2)


def http_reply(payload=None, error=None):
    response = mock.Mock()
    if isinstance(error, Exception):
        return mock.Mock(side_effect=error)
    response.json.return_value = payload
    return mock.Mock(return_value=response)


class TestStatusPages(Base):
    GET = "uptime_kuma_api._mixins.status_pages.requests.get"

    def setUp(self):
        super().setUp()
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
        self.assertEqual(self.api.get_status_pages(), [{"id": 5, "slug": "s"}])

    def test_get_status_page_combines_both_sources(self):
        with mock.patch(self.GET, http_reply(self.page)) as get:
            page = self.api.get_status_page("a/b")
        self.assertIn("a%2Fb", get.call_args.args[0])
        self.assertEqual(page["icon"], "/i.svg")
        self.assertEqual(page["incident"]["style"], IncidentStyle.DANGER)
        self.assertEqual(len(page["incidents"]), 1)
        self.assertIs(page["publicGroupList"][0]["monitorList"][0]["sendUrl"],
                      True)

    def test_get_status_page_without_incident(self):
        self.page.pop("incident")
        with mock.patch(self.GET, http_reply(self.page)):
            page = self.api.get_status_page("s")
        self.assertIsNone(page["incident"])
        self.assertEqual(page["incidents"], [])

    def test_http_errors_are_mapped(self):
        cases = [
            (requests.exceptions.Timeout("t"), Timeout),
            (requests.exceptions.ConnectionError("c"), UptimeKumaException),
            (ValueError("not json"), UptimeKumaException),
        ]
        for error, expected in cases:
            with self.subTest(error=type(error).__name__):
                with mock.patch(self.GET, http_reply(error=error)):
                    with self.assertRaises(expected):
                        self.api.get_status_page("s")

    def test_add_and_delete(self):
        self.data[Event.STATUS_PAGE_LIST] = {"5": {"id": 5, "slug": "s"}}
        self.api.add_status_page("new", "New")
        self.assertEqual(self.sio.sent("addStatusPage"), [("New", "new")])
        self.api.delete_status_page("s")
        self.assertEqual(self.sio.sent("deleteStatusPage"), ["s"])
        self.assertEqual(self.data[Event.STATUS_PAGE_LIST], {})
        with self.assertRaises(UptimeKumaException):
            self.api.delete_status_page("s")

    def test_save_round_trips_the_page_and_updates_the_cache(self):
        with mock.patch(self.GET, http_reply(self.page)):
            self.api.save_status_page("s", title="new")
            self.api.save_status_page(
                "s", publicGroupList=[{"name": "other", "monitorList": []}])
        first, second = self.sio.sent("saveStatusPage")
        self.assertEqual(first[1]["title"], "new")
        self.assertEqual(first[3][0]["name"], "g")
        self.assertEqual(second[3][0]["name"], "other")
        self.assertNotIn("incident", first[1])
        self.assertEqual(self.data[Event.STATUS_PAGE_LIST]["5"]["id"], 5)

    def test_post_and_unpin_incident(self):
        self.sio.replies["postIncident"] = {
            "ok": True, "incident": {"id": 1, "style": "info"}}
        with mock.patch(self.GET, http_reply(self.page)):
            incident = self.api.post_incident("s", "t", "c",
                                              IncidentStyle.INFO)
            self.api.unpin_incident("s")
        self.assertEqual(incident["style"], IncidentStyle.INFO)
        self.assertEqual(self.sio.sent("postIncident")[0][1]["title"], "t")
        self.assertEqual(self.sio.sent("unpinIncident"), ["s"])
        self.assertEqual(len(self.sio.sent("saveStatusPage")), 2)

    def test_build_status_page_data(self):
        slug, config, icon, groups = self.api._build_status_page_data(
            "s", id=1, title="t")
        self.assertEqual((slug, config["theme"], icon, groups),
                         ("s", "auto", "/icon.svg", []))
        self.assertIn("showCertificateExpiry", config)
        with self.assertRaises(ValueError):
            self.api._build_status_page_data("s", id=1, title="t",
                                             theme="neon")

    def test_old_servers_default_to_the_light_theme(self):
        self.data[Event.INFO] = {"version": "1.21.0"}
        self.api._version = None
        _, config, _, _ = self.api._build_status_page_data(
            "s", id=1, title="t")
        self.assertEqual(config["theme"], "light")
        self.assertNotIn("showCertificateExpiry", config)


if __name__ == "__main__":
    unittest.main()
