import contextlib
import threading
import time
import unittest
from unittest import mock

import requests

from uptime_kuma_api import (
    Event, Timeout, UptimeKumaApi, UptimeKumaException,
    MaintenanceStrategy, MonitorStatus, MonitorType, NotificationType,
)
from uptime_kuma_api.api import (
    _build_notification_data,
    _check_argument_conditions,
    _check_arguments_maintenance,
    _check_arguments_monitor,
    _check_arguments_notification,
    _check_arguments_proxy,
    _check_arguments_tag,
    _build_status_page_response,
    _check_missing_arguments,
    _merge_settings,
    _warned_values,
    _convert_monitor_input,
    gen_secret,
    int_to_bool,
    parse_monitor_status,
    parse_value,
)


class TestParsing(unittest.TestCase):
    def test_int_to_bool_dict_and_list(self):
        d = {"a": 1, "b": 0, "c": 5}
        int_to_bool(d, ["a", "b", "c", "missing"])
        self.assertEqual(d, {"a": True, "b": False, "c": False})
        rows = [{"a": 1}, {"a": 0}]
        int_to_bool(rows, ["a"])
        self.assertEqual(rows, [{"a": True}, {"a": False}])

    def test_parse_value_enum_default_and_invalid(self):
        d = {"status": 1}
        parse_monitor_status(d)
        self.assertIs(d["status"], MonitorStatus.UP)
        d = {"x": None}
        parse_value(d, "x", int, default=7)
        self.assertEqual(d["x"], 7)
        d = {"status": 99}  # unknown value is left untouched
        parse_monitor_status(d)
        self.assertEqual(d["status"], 99)
        parse_value(None, "x", int)  # falsy data is a no-op

    def test_gen_secret(self):
        s = gen_secret(32)
        self.assertEqual(len(s), 32)
        self.assertTrue(s.isalnum())
        self.assertNotEqual(s, gen_secret(32))

DATABASE_TYPES = (
    MonitorType.SQLSERVER, MonitorType.POSTGRES, MonitorType.MYSQL,
    MonitorType.MONGODB, MonitorType.REDIS,
)


class TestConvertMonitorInput(unittest.TestCase):
    def kwargs(self, **kw):
        base = dict(accepted_statuscodes=None, notificationIDList=None,
                    databaseConnectionString=None, type=MonitorType.HTTP)
        base.update(kw)
        return base

    def test_defaults(self):
        k = self.kwargs(notificationIDList=[1, 2])
        _convert_monitor_input(k)
        self.assertEqual(k["accepted_statuscodes"], ["200-299"])
        self.assertEqual(k["notificationIDList"], {1: True, 2: True})

    def test_push_token_generated(self):
        k = self.kwargs(type=MonitorType.PUSH)
        _convert_monitor_input(k)
        self.assertEqual(len(k["pushToken"]), 32)
        k = self.kwargs(type=MonitorType.PUSH, pushToken="mine")
        _convert_monitor_input(k)
        self.assertEqual(k["pushToken"], "mine")

    def test_no_placeholder_connection_string(self):
        for t in DATABASE_TYPES:
            k = self.kwargs(type=t)
            _convert_monitor_input(k)
            self.assertIsNone(k["databaseConnectionString"], t)


class TestChecks(unittest.TestCase):
    def test_missing_arguments(self):
        with self.assertRaises(TypeError):
            _check_missing_arguments(["a", "b"], {"a": 1})
        _check_missing_arguments(["a"], {"a": 0})  # 0 is a value

    def test_conditions(self):
        c = {"n": dict(min=1, max=3)}
        _check_argument_conditions(c, {"n": 2})
        _check_argument_conditions(c, {"n": None})
        _check_argument_conditions(c, {})
        for bad in (0, 4):
            with self.assertRaises(ValueError):
                _check_argument_conditions(c, {"n": bad})

    def monitor(self, **kw):
        base = dict(type=MonitorType.PUSH, name="n", interval=60, maxretries=0, retryInterval=60,
                    accepted_statuscodes=["200-299"], dns_resolve_type="A",
                    kafkaProducerSaslOptions={"mechanism": "None"})
        base.update(kw)
        return base

    def test_monitor_ok_and_required_by_type(self):
        _check_arguments_monitor(self.monitor())
        with self.assertRaises(TypeError):
            _check_arguments_monitor(self.monitor(type=MonitorType.PORT))
        _check_arguments_monitor(self.monitor(type=MonitorType.PORT, hostname="h", port=80))

    def test_monitor_ranges(self):
        with self.assertRaises(ValueError):
            _check_arguments_monitor(self.monitor(interval=19))
        with self.assertRaises(ValueError):
            _check_arguments_monitor(self.monitor(type=MonitorType.PORT, hostname="h", port=70000))

    def test_database_types_require_connection_string(self):
        for t in DATABASE_TYPES:
            with self.assertRaisesRegex(TypeError, "databaseConnectionString"):
                _check_arguments_monitor(self.monitor(type=t))
            _check_arguments_monitor(
                self.monitor(type=t, databaseConnectionString="x"))

    def test_unknown_type_raises_clean_error(self):
        with self.assertRaisesRegex(ValueError, "unsupported monitor type: ntp"):
            _check_arguments_monitor(self.monitor(type="ntp"))

    def test_statuscode_error_names_the_offending_value(self):
        for good in ("200", "999", "100-199", "500-599"):
            _check_arguments_monitor(self.monitor(accepted_statuscodes=[good]))
        for bad in ("1000", "99", "foo", "200-300"):
            with self.assertRaises(ValueError) as cm:
                _check_arguments_monitor(self.monitor(accepted_statuscodes=[bad]))
            self.assertIn(repr(bad), str(cm.exception))
            self.assertLess(len(str(cm.exception)), 200)

    def test_kafka_sasl_options_missing_or_none_means_no_mechanism(self):
        kafka = dict(type=MonitorType.KAFKA_PRODUCER, kafkaProducerTopic="t",
                     kafkaProducerMessage="m")
        for opts in (None, {}, {"mechanism": None}, {"mechanism": "plain"}):
            _check_arguments_monitor(self.monitor(kafkaProducerSaslOptions=opts, **kafka))
        _check_arguments_monitor(self.monitor(**kafka))
        with self.assertRaises(ValueError):
            _check_arguments_monitor(
                self.monitor(kafkaProducerSaslOptions={"mechanism": "x"}, **kafka))

    def test_status_page_theme_error_lists_valid_themes(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        with self.assertRaisesRegex(ValueError, "Valid themes: auto, light, dark"):
            api._build_status_page_data("s", id=1, title="t", theme="neon")

    def test_every_monitor_type_has_required_args_entry(self):
        for t in MonitorType:
            try:
                _check_arguments_monitor(self.monitor(type=t))
            except (TypeError, ValueError) as e:
                if "unsupported monitor type" in str(e):
                    self.fail(f"{t} missing from required_args_by_type")

    def test_proxy(self):
        ok = dict(protocol="http", host="h", port=8080)
        _check_arguments_proxy(ok)
        with self.assertRaises(TypeError):
            _check_arguments_proxy(dict(ok, auth=True))
        with self.assertRaises(ValueError):
            _check_arguments_proxy(dict(ok, port=65536))

    def test_maintenance(self):
        _check_arguments_maintenance(dict(title="t", strategy=MaintenanceStrategy.MANUAL))
        with self.assertRaises(TypeError):
            _check_arguments_maintenance(dict(title="t", strategy=MaintenanceStrategy.RECURRING_INTERVAL))
        with self.assertRaises(ValueError):
            _check_arguments_maintenance(dict(title="t", strategy=MaintenanceStrategy.MANUAL, intervalDay=0))

    def test_tag(self):
        _check_arguments_tag(dict(name="n", color="#fff"))
        with self.assertRaises(TypeError):
            _check_arguments_tag(dict(name="n"))

    def test_notification(self):
        ok = dict(type=NotificationType.WEBHOOK, name="n",
                  webhookContentType="json", webhookURL="http://x")
        _check_arguments_notification(ok)
        with self.assertRaises(TypeError):
            _check_arguments_notification(dict(type=NotificationType.WEBHOOK, name="n"))
        with self.assertRaises(TypeError):
            _check_arguments_notification(dict(type=NotificationType.WEBHOOK))


class TestBuildNotificationData(unittest.TestCase):
    def test_defaults_and_kwargs(self):
        d = _build_notification_data("n", NotificationType.WEBHOOK, webhookURL="u")
        self.assertEqual(d, dict(name="n", type=NotificationType.WEBHOOK, isDefault=False,
                                 applyExisting=False, webhookURL="u"))

    def test_unknown_argument(self):
        with self.assertRaises(TypeError):
            _build_notification_data("n", NotificationType.WEBHOOK, nope=1)


class TestStatusPageResponse(unittest.TestCase):
    inc = {"id": 1, "style": "danger", "title": "t"}

    def test_2_5_incidents_list(self):
        d = _build_status_page_response({}, {"incidents": [dict(self.inc)]})
        self.assertEqual(len(d["incidents"]), 1)
        self.assertEqual(d["incident"]["id"], 1)
        self.assertEqual(d["incident"]["style"].value, "danger")

    def test_legacy_incident(self):
        d = _build_status_page_response({}, {"incident": dict(self.inc)})
        self.assertEqual(d["incidents"][0]["id"], 1)

    def test_none(self):
        d = _build_status_page_response({}, {})
        self.assertEqual((d["incident"], d["incidents"]), (None, []))


class TestSaveStatusPage(unittest.TestCase):
    def test_derived_keys_not_sent(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._event_data = {Event.STATUS_PAGE_LIST: {}}
        page = {"id": 1, "incident": {}, "incidents": [{}], "maintenanceList": [],
                "publicGroupList": [], "title": "t"}
        api.get_status_page = lambda slug: dict(page)
        sent = []
        api._call = lambda event, data=None: (
            sent.append((event, data)) or {"config": {"id": 1}})
        api.save_status_page("s")
        config = sent[0][1][1]
        for key in ("incident", "incidents", "maintenanceList", "publicGroupList"):
            self.assertNotIn(key, config)


class TestMonitorListDeltaEvents(unittest.TestCase):
    def api(self, monitors):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._event_data = {Event.MONITOR_LIST: monitors}
        api._event_seq = dict.fromkeys(api._event_data, 0)
        return api

    def test_update_adds_and_replaces(self):
        api = self.api({"1": {"name": "a"}})
        api._event_update_monitor_into_list({"1": {"name": "b"}, "2": {"name": "c"}})
        self.assertEqual(api._event_data[Event.MONITOR_LIST],
                         {"1": {"name": "b"}, "2": {"name": "c"}})

    def test_delete_removes_and_ignores_unknown(self):
        api = self.api({"1": {}, "2": {}})
        api._event_delete_monitor_from_list(1)
        api._event_delete_monitor_from_list(99)
        self.assertEqual(list(api._event_data[Event.MONITOR_LIST]), ["2"])

    def test_noop_before_initial_list(self):
        api = self.api(None)
        api._event_update_monitor_into_list({"1": {}})
        api._event_delete_monitor_from_list(1)
        self.assertIsNone(api._event_data[Event.MONITOR_LIST])


class TestGetStatusPageHttp(unittest.TestCase):
    def api(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api.url = "https://kuma"
        api.timeout = 5
        api.ssl_verify = False
        api.headers = {"X-Auth": "t"}
        api._call = lambda event, slug: {"config": {}}
        return api

    @mock.patch("uptime_kuma_api.api.requests.get")
    def test_passes_verify_headers_and_escaped_slug(self, get):
        get.return_value.json.return_value = {}
        self.api().get_status_page("a/../b?x")
        get.assert_called_once_with(
            "https://kuma/api/status-page/a%2F..%2Fb%3Fx",
            timeout=5, verify=False, headers={"X-Auth": "t"})

    @mock.patch("uptime_kuma_api.api.requests.get")
    def test_error_mapping(self, get):
        cases = [
            (requests.exceptions.Timeout("t"), Timeout),
            (requests.exceptions.ConnectionError("c"), UptimeKumaException),
            (requests.exceptions.SSLError("s"), UptimeKumaException),
        ]
        for exc, expected in cases:
            get.side_effect = exc
            with self.assertRaises(expected) as cm:
                self.api().get_status_page("s")
            self.assertIs(cm.exception.__cause__, exc)

    @mock.patch("uptime_kuma_api.api.requests.get")
    def test_invalid_json(self, get):
        get.return_value.json.side_effect = ValueError("not json")
        with self.assertRaises(UptimeKumaException):
            self.api().get_status_page("s")


class TestMergeSettings(unittest.TestCase):
    def test_only_non_none_override(self):
        cur = {"keepDataPeriodDays": 30, "trustProxy": True}
        d = _merge_settings(cur, {"checkUpdate": False, "keepDataPeriodDays": None, "trustProxy": None})
        self.assertEqual(d["keepDataPeriodDays"], 30)
        self.assertIs(d["trustProxy"], True)
        self.assertIs(d["checkUpdate"], False)

    def test_falsy_values_override(self):
        d = _merge_settings({"keepDataPeriodDays": 30, "steamAPIKey": "x"}, {"keepDataPeriodDays": 0, "steamAPIKey": ""})
        self.assertEqual((d["keepDataPeriodDays"], d["steamAPIKey"]), (0, ""))

    def test_entry_page_fallback(self):
        self.assertEqual(_merge_settings({}, {})["entryPage"], "dashboard")


class TestLoginAutoLogin(unittest.TestCase):
    def test_timeout_message_mentions_credentials(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._event_data = {Event.AUTO_LOGIN: None}
        api._event_seq = dict.fromkeys(api._event_data, 0)
        api.timeout = 0.05
        with self.assertRaises(Timeout) as cm:
            api.login()
        self.assertIn("username and password", str(cm.exception))


class TestHeartbeatCap(unittest.TestCase):
    def test_keeps_150_newest_last(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._event_data = {Event.HEARTBEAT_LIST: None,
                           Event.IMPORTANT_HEARTBEAT_LIST: None}
        for i in range(200):
            api._event_heartbeat({"monitorID": 1, "important": False, "id": i})
        beats = api._event_data[Event.HEARTBEAT_LIST][1]
        self.assertEqual(len(beats), 150)
        self.assertEqual((beats[0]["id"], beats[-1]["id"]), (50, 199))


class TestAddMonitorTagCache(unittest.TestCase):
    def api(self, cache):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._event_data = {Event.MONITOR_LIST: cache}
        api._event_seq = dict.fromkeys(api._event_data, 0)
        raw = {"id": 1, "notificationIDList": {"3": True}}
        api._call = lambda event, data=None: (
            {"monitor": raw} if event == "getMonitor" else {"msg": "ok"})
        return api, raw

    def test_none_cache_does_not_raise(self):
        api, _ = self.api(None)
        api.add_monitor_tag(1, 1)
        self.assertIsNone(api._event_data[Event.MONITOR_LIST])

    def test_cache_gets_raw_monitor(self):
        api, raw = self.api({})
        api.add_monitor_tag(1, 1)
        self.assertIs(api._event_data[Event.MONITOR_LIST]["1"], raw)
        self.assertEqual(raw["notificationIDList"], {"3": True})

    def delete_api(self, cache):
        api, raw = self.api(cache)
        api.wait_for_event = lambda event: contextlib.nullcontext()
        api.get_monitors = lambda: [{"tags": [
            {"monitor_id": 1, "tag_id": 1, "value": ""}]}]
        return api, raw

    def test_delete_returns_response_with_none_cache(self):
        api, _ = self.delete_api(None)
        self.assertEqual(api.delete_monitor_tag(1, 1), {"msg": "ok"})
        self.assertIsNone(api._event_data[Event.MONITOR_LIST])

    def test_delete_caches_raw_monitor(self):
        api, raw = self.delete_api({})
        self.assertEqual(api.delete_monitor_tag(1, 1), {"msg": "ok"})
        self.assertIs(api._event_data[Event.MONITOR_LIST]["1"], raw)


class TestUnknownEnumLogging(unittest.TestCase):
    def setUp(self):
        _warned_values.clear()

    def test_warns_once_and_keeps_raw_value(self):
        d = {"type": "brand-new-type"}
        with self.assertLogs("uptime_kuma_api.api", "WARNING") as cm:
            parse_value(d, "type", MonitorType)
        self.assertEqual(d["type"], "brand-new-type")
        self.assertIn("brand-new-type", cm.output[0])
        with self.assertNoLogs("uptime_kuma_api.api", "WARNING"):
            parse_value(dict(d), "type", MonitorType)


if __name__ == "__main__":
    unittest.main()


class TestVersionCache(unittest.TestCase):
    def _api(self, info):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api.timeout = 0.05
        api.wait_events = 5
        api._version = None
        api._event_data = {Event.INFO: info}
        return api

    def test_version_is_cached_and_does_not_sleep(self):
        api = self._api({"version": "2.5.6"})
        with mock.patch.object(api, "_get_event_data") as get, \
                mock.patch("time.sleep") as sleep:
            self.assertEqual(api.version, "2.5.6")
            api._event_data[Event.INFO] = {"version": "9.9.9"}
            self.assertEqual(api.version, "2.5.6")
        get.assert_not_called()
        sleep.assert_not_called()

    def test_new_info_event_resets_cache(self):
        api = self._api({"version": "2.5.6"})
        self.assertEqual(api.version, "2.5.6")
        api._event_info({"version": "2.6.0"})
        self.assertEqual(api.version, "2.6.0")

    def test_times_out_without_info(self):
        with self.assertRaises(Timeout):
            _ = self._api(None).version


class TestWaitForNewEvent(unittest.TestCase):
    def _api(self, timeout=1):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api.timeout = timeout
        api._event_data = {Event.NOTIFICATION_LIST: []}
        api._event_seq = dict.fromkeys(api._event_data, 0)
        return api

    def test_blocks_until_new_event_arrives(self):
        api = self._api()
        timer = threading.Timer(
            0.2, api._event_notification_list, args=([{"id": 1}],))
        timer.start()
        start = time.time()
        with api.wait_for_event(Event.NOTIFICATION_LIST, new=True):
            pass
        self.assertGreaterEqual(time.time() - start, 0.15)
        self.assertEqual(api._event_data[Event.NOTIFICATION_LIST], [{"id": 1}])

    def test_event_during_body_counts(self):
        api = self._api()
        with api.wait_for_event(Event.NOTIFICATION_LIST, new=True):
            api._event_notification_list([])

    def test_times_out_without_new_event(self):
        api = self._api(timeout=0.05)
        with self.assertRaises(Timeout):
            with api.wait_for_event(Event.NOTIFICATION_LIST, new=True):
                pass

    def test_body_error_propagates_without_waiting(self):
        api = self._api(timeout=0.05)
        with self.assertRaises(UptimeKumaException):
            with api.wait_for_event(Event.NOTIFICATION_LIST, new=True):
                raise UptimeKumaException("nope")

    def test_old_event_does_not_count_by_default(self):
        api = self._api(timeout=0.05)
        with api.wait_for_event(Event.NOTIFICATION_LIST):
            pass  # data already present, no new event needed
