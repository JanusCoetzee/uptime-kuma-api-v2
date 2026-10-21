import contextlib
import logging
import threading
import time
from unittest import mock

import pytest
import requests
import socketio

from uptime_kuma_api import (
    AuthMethod, Event, Timeout, UptimeKumaApi, UptimeKumaConnectionError,
    UptimeKumaException,
    MaintenanceStrategy, MonitorStatus, MonitorType, NotificationType,
)
from uptime_kuma_api._helpers import (
    _check_argument_conditions,
    _check_missing_arguments,
    _warned_values,
    int_to_bool,
    parse_monitor_status,
    parse_value,
)
from uptime_kuma_api._mixins.maintenance import _check_arguments_maintenance
from uptime_kuma_api._monitor_args import (
    _check_arguments_monitor,
    _convert_monitor_input,
    gen_secret,
)
from uptime_kuma_api._mixins.notifications import (
    _build_notification_data,
    _check_arguments_notification,
)
from uptime_kuma_api._mixins.proxies import _check_arguments_proxy
from uptime_kuma_api._mixins.settings import _merge_settings
from uptime_kuma_api._mixins.status_pages import _build_status_page_response
from uptime_kuma_api._mixins.tags import _check_arguments_tag


class TestParsing:
    def test_int_to_bool_dict_and_list(self):
        d = {"a": 1, "b": 0, "c": 5}
        int_to_bool(d, ["a", "b", "c", "missing"])
        assert d == {"a": True, "b": False, "c": False}
        rows = [{"a": 1}, {"a": 0}]
        int_to_bool(rows, ["a"])
        assert rows == [{"a": True}, {"a": False}]

    def test_parse_value_enum_default_and_invalid(self):
        d = {"status": 1}
        parse_monitor_status(d)
        assert d["status"] is MonitorStatus.UP
        d = {"x": None}
        parse_value(d, "x", int, default=7)
        assert d["x"] == 7
        d = {"status": 99}  # unknown value is left untouched
        parse_monitor_status(d)
        assert d["status"] == 99
        parse_value(None, "x", int)  # falsy data is a no-op

    def test_gen_secret(self):
        s = gen_secret(32)
        assert len(s) == 32
        assert s.isalnum()
        assert s != gen_secret(32)


DATABASE_TYPES = (
    MonitorType.SQLSERVER, MonitorType.POSTGRES, MonitorType.MYSQL,
    MonitorType.MONGODB, MonitorType.REDIS,
)


class TestConvertMonitorInput:
    def kwargs(self, **kw):
        base = dict(accepted_statuscodes=None, notificationIDList=None,
                    databaseConnectionString=None, type=MonitorType.HTTP)
        base.update(kw)
        return base

    def test_defaults(self):
        k = self.kwargs(notificationIDList=[1, 2])
        _convert_monitor_input(k)
        assert k["accepted_statuscodes"] == ["200-299"]
        assert k["notificationIDList"] == {1: True, 2: True}

    def test_push_token_generated(self):
        k = self.kwargs(type=MonitorType.PUSH)
        _convert_monitor_input(k)
        assert len(k["pushToken"]) == 32
        k = self.kwargs(type=MonitorType.PUSH, pushToken="mine")
        _convert_monitor_input(k)
        assert k["pushToken"] == "mine"

    def test_no_placeholder_connection_string(self):
        for t in DATABASE_TYPES:
            k = self.kwargs(type=t)
            _convert_monitor_input(k)
            assert k["databaseConnectionString"] is None


class TestChecks:
    def test_missing_arguments(self):
        with pytest.raises(TypeError):
            _check_missing_arguments(["a", "b"], {"a": 1})
        _check_missing_arguments(["a"], {"a": 0})  # 0 is a value

    def test_conditions(self):
        c = {"n": dict(min=1, max=3)}
        _check_argument_conditions(c, {"n": 2})
        _check_argument_conditions(c, {"n": None})
        _check_argument_conditions(c, {})
        for bad in (0, 4):
            with pytest.raises(ValueError):
                _check_argument_conditions(c, {"n": bad})

    def monitor(self, **kw):
        base = dict(
            type=MonitorType.PUSH,
            name="n",
            interval=60,
            maxretries=0,
            retryInterval=60,
            accepted_statuscodes=["200-299"],
            dns_resolve_type="A",
            kafkaProducerSaslOptions={"mechanism": "None"},
        )
        base.update(kw)
        return base

    def test_monitor_ok_and_required_by_type(self):
        _check_arguments_monitor(self.monitor())
        with pytest.raises(TypeError):
            _check_arguments_monitor(self.monitor(type=MonitorType.PORT))
        _check_arguments_monitor(
            self.monitor(type=MonitorType.PORT, hostname="h", port=80)
        )

    def test_monitor_ranges(self):
        with pytest.raises(ValueError):
            _check_arguments_monitor(self.monitor(interval=19))
        with pytest.raises(ValueError):
            _check_arguments_monitor(
                self.monitor(type=MonitorType.PORT, hostname="h", port=70000)
            )

    def test_database_types_require_connection_string(self):
        for t in DATABASE_TYPES:
            with pytest.raises(TypeError, match="databaseConnectionString"):
                _check_arguments_monitor(self.monitor(type=t))
            _check_arguments_monitor(
                self.monitor(type=t, databaseConnectionString="x"))

    def test_unknown_type_raises_clean_error(self):
        with pytest.raises(
            ValueError, match="unsupported monitor type: not-a-type"
        ):
            _check_arguments_monitor(self.monitor(type="not-a-type"))

    def test_statuscode_error_names_the_offending_value(self):
        for good in ("200", "999", "100-199", "500-599"):
            _check_arguments_monitor(self.monitor(accepted_statuscodes=[good]))
        for bad in ("1000", "99", "foo", "200-300"):
            with pytest.raises(ValueError) as cm:
                _check_arguments_monitor(self.monitor(accepted_statuscodes=[bad]))
            assert repr(bad) in str(cm.value)
            assert len(str(cm.value)) < 200

    def test_kafka_sasl_options_missing_or_none_means_no_mechanism(self):
        kafka = dict(type=MonitorType.KAFKA_PRODUCER, kafkaProducerTopic="t",
                     kafkaProducerMessage="m")
        for opts in (None, {}, {"mechanism": None}, {"mechanism": "plain"}):
            _check_arguments_monitor(
                self.monitor(kafkaProducerSaslOptions=opts, **kafka)
            )
        _check_arguments_monitor(self.monitor(**kafka))
        for bad in ("x", ""):
            with pytest.raises(ValueError):
                _check_arguments_monitor(
                    self.monitor(
                        kafkaProducerSaslOptions={"mechanism": bad}, **kafka
                    )
                )

    def test_status_page_theme_error_lists_valid_themes(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
        with pytest.raises(
            ValueError, match="Valid themes: auto, light, dark"
        ):
            api._build_status_page_data("s", id=1, title="t", theme="neon")

    def test_every_monitor_type_has_required_args_entry(self):
        for t in MonitorType:
            try:
                _check_arguments_monitor(self.monitor(type=t))
            except (TypeError, ValueError) as e:
                if "unsupported monitor type" in str(e):
                    pytest.fail(f"{t} missing from required_args_by_type")

    def test_unknown_monitor_type_is_rejected_clearly(self):
        with pytest.raises(ValueError, match="^unsupported monitor type: "):
            _check_arguments_monitor(self.monitor(type="bogus"))

    def test_proxy(self):
        ok = dict(protocol="http", host="h", port=8080)
        _check_arguments_proxy(ok)
        with pytest.raises(TypeError):
            _check_arguments_proxy(dict(ok, auth=True))
        with pytest.raises(ValueError):
            _check_arguments_proxy(dict(ok, port=65536))

    def test_maintenance(self):
        _check_arguments_maintenance(
            dict(title="t", strategy=MaintenanceStrategy.MANUAL)
        )
        with pytest.raises(TypeError):
            _check_arguments_maintenance(
                dict(
                    title="t", strategy=MaintenanceStrategy.RECURRING_INTERVAL
                )
            )
        with pytest.raises(ValueError):
            _check_arguments_maintenance(
                dict(
                    title="t",
                    strategy=MaintenanceStrategy.MANUAL,
                    intervalDay=0,
                )
            )

    def test_tag(self):
        _check_arguments_tag(dict(name="n", color="#fff"))
        with pytest.raises(TypeError):
            _check_arguments_tag(dict(name="n"))

    def test_notification(self):
        ok = dict(type=NotificationType.WEBHOOK, name="n",
                  webhookContentType="json", webhookURL="http://x")
        _check_arguments_notification(ok)
        with pytest.raises(TypeError):
            _check_arguments_notification(
                dict(type=NotificationType.WEBHOOK, name="n")
            )
        with pytest.raises(TypeError):
            _check_arguments_notification(dict(type=NotificationType.WEBHOOK))


class TestBuildNotificationData:
    def test_defaults_and_kwargs(self):
        d = _build_notification_data(
            "n", NotificationType.WEBHOOK, webhookURL="u"
        )
        assert d == dict(
            name="n",
            type=NotificationType.WEBHOOK,
            isDefault=False,
            applyExisting=False,
            webhookURL="u",
        )

    def test_unknown_argument(self):
        with pytest.raises(TypeError):
            _build_notification_data("n", NotificationType.WEBHOOK, nope=1)


class TestStatusPageResponse:
    inc = {"id": 1, "style": "danger", "title": "t"}

    def test_2_5_incidents_list(self):
        d = _build_status_page_response({}, {"incidents": [dict(self.inc)]})
        assert len(d["incidents"]) == 1
        assert d["incident"]["id"] == 1
        assert d["incident"]["style"].value == "danger"

    def test_legacy_incident(self):
        d = _build_status_page_response({}, {"incident": dict(self.inc)})
        assert d["incidents"][0]["id"] == 1

    def test_none(self):
        d = _build_status_page_response({}, {})
        assert (d["incident"], d["incidents"]) == (None, [])


class TestSaveStatusPage:
    def test_derived_keys_not_sent(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
        api._event_data = {Event.STATUS_PAGE_LIST: {}}
        page = {
            "id": 1,
            "incident": {},
            "incidents": [{}],
            "maintenanceList": [],
            "publicGroupList": [],
            "title": "t",
        }
        api.get_status_page = lambda slug: dict(page)
        sent = []
        api._call = lambda event, data=None: (
            sent.append((event, data)) or {"config": {"id": 1}})
        api.save_status_page("s")
        config = sent[0][1][1]
        for key in (
            "incident",
            "incidents",
            "maintenanceList",
            "publicGroupList",
        ):
            assert key not in config


class TestMonitorListDeltaEvents:
    def api(self, monitors):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
        api._event_data = {Event.MONITOR_LIST: monitors}
        api._event_seq = dict.fromkeys(api._event_data, 0)
        return api

    def test_update_adds_and_replaces(self):
        api = self.api({"1": {"name": "a"}})
        api._event_update_monitor_into_list(
            {"1": {"name": "b"}, "2": {"name": "c"}}
        )
        assert api._event_data[Event.MONITOR_LIST] == {
            "1": {"name": "b"},
            "2": {"name": "c"},
        }

    def test_delete_removes_and_ignores_unknown(self):
        api = self.api({"1": {}, "2": {}})
        api._event_delete_monitor_from_list(1)
        api._event_delete_monitor_from_list(99)
        assert list(api._event_data[Event.MONITOR_LIST]) == ["2"]

    def test_noop_before_initial_list(self):
        api = self.api(None)
        api._event_update_monitor_into_list({"1": {}})
        api._event_delete_monitor_from_list(1)
        assert api._event_data[Event.MONITOR_LIST] is None


class TestGetStatusPageHttp:
    def api(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
        api.url = "https://kuma"
        api.timeout = 5
        api.ssl_verify = False
        api.headers = {"X-Auth": "t"}
        api._call = lambda event, slug: {"config": {}}
        return api

    @mock.patch("uptime_kuma_api._mixins.status_pages.requests.get")
    def test_passes_verify_headers_and_escaped_slug(self, get):
        get.return_value.json.return_value = {}
        self.api().get_status_page("a/../b?x")
        get.assert_called_once_with(
            "https://kuma/api/status-page/a%2F..%2Fb%3Fx",
            timeout=5, verify=False, headers={"X-Auth": "t"})

    @mock.patch("uptime_kuma_api._mixins.status_pages.requests.get")
    def test_error_mapping(self, get):
        cases = [
            (requests.exceptions.Timeout("t"), Timeout),
            (requests.exceptions.ConnectionError("c"), UptimeKumaException),
            (requests.exceptions.SSLError("s"), UptimeKumaException),
        ]
        for exc, expected in cases:
            get.side_effect = exc
            with pytest.raises(expected) as cm:
                self.api().get_status_page("s")
            assert cm.value.__cause__ is exc

    @mock.patch("uptime_kuma_api._mixins.status_pages.requests.get")
    def test_invalid_json(self, get):
        get.return_value.json.side_effect = ValueError("not json")
        with pytest.raises(UptimeKumaException):
            self.api().get_status_page("s")


class TestMergeSettings:
    def test_only_non_none_override(self):
        cur = {"keepDataPeriodDays": 30, "trustProxy": True}
        d = _merge_settings(
            cur,
            {
                "checkUpdate": False,
                "keepDataPeriodDays": None,
                "trustProxy": None,
            },
        )
        assert d["keepDataPeriodDays"] == 30
        assert d["trustProxy"] is True
        assert d["checkUpdate"] is False

    def test_falsy_values_override(self):
        d = _merge_settings(
            {"keepDataPeriodDays": 30, "steamAPIKey": "x"},
            {"keepDataPeriodDays": 0, "steamAPIKey": ""},
        )
        assert (d["keepDataPeriodDays"], d["steamAPIKey"]) == (0, "")

    def test_entry_page_fallback(self):
        assert _merge_settings({}, {})["entryPage"] == "dashboard"


class TestLoginAutoLogin:
    def test_timeout_message_mentions_credentials(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
        api._event_data = {Event.AUTO_LOGIN: None}
        api._event_seq = dict.fromkeys(api._event_data, 0)
        api.timeout = 0.05
        with pytest.raises(Timeout) as cm:
            api.login()
        assert "username and password" in str(cm.value)


class TestHeartbeatCap:
    def test_keeps_150_newest_last(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
        api._event_data = {Event.HEARTBEAT_LIST: None,
                           Event.IMPORTANT_HEARTBEAT_LIST: None}
        for i in range(200):
            api._event_heartbeat({"monitorID": 1, "important": False, "id": i})
        beats = api._event_data[Event.HEARTBEAT_LIST][1]
        assert len(beats) == 150
        assert (beats[0]["id"], beats[-1]["id"]) == (50, 199)


class TestAddMonitorTagCache:
    def api(self, cache):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
        api._event_data = {Event.MONITOR_LIST: cache}
        api._event_seq = dict.fromkeys(api._event_data, 0)
        raw = {"id": 1, "notificationIDList": {"3": True}}
        api._call = lambda event, data=None: (
            {"monitor": raw} if event == "getMonitor" else {"msg": "ok"})
        return api, raw

    def test_none_cache_does_not_raise(self):
        api, _ = self.api(None)
        api.add_monitor_tag(1, 1)
        assert api._event_data[Event.MONITOR_LIST] is None

    def test_cache_gets_raw_monitor(self):
        api, raw = self.api({})
        api.add_monitor_tag(1, 1)
        assert api._event_data[Event.MONITOR_LIST]["1"] is raw
        assert raw["notificationIDList"] == {"3": True}

    def delete_api(self, cache):
        api, raw = self.api(cache)
        api.wait_for_event = lambda event: contextlib.nullcontext()
        api.get_monitors = lambda: [{"tags": [
            {"monitor_id": 1, "tag_id": 1, "value": ""}]}]
        return api, raw

    def test_delete_returns_response_with_none_cache(self):
        api, _ = self.delete_api(None)
        assert api.delete_monitor_tag(1, 1) == {"msg": "ok"}
        assert api._event_data[Event.MONITOR_LIST] is None

    def test_delete_caches_raw_monitor(self):
        api, raw = self.delete_api({})
        assert api.delete_monitor_tag(1, 1) == {"msg": "ok"}
        assert api._event_data[Event.MONITOR_LIST]["1"] is raw


class TestUnknownEnumLogging:
    @pytest.fixture(autouse=True)
    def _setup(self):
        _warned_values.clear()

    def test_warns_once_and_keeps_raw_value(self, caplog):
        caplog.set_level(logging.WARNING, logger="uptime_kuma_api.api")
        d = {"type": "brand-new-type"}
        parse_value(d, "type", MonitorType)
        assert d["type"] == "brand-new-type"
        assert len(caplog.records) == 1
        assert "brand-new-type" in caplog.records[0].getMessage()
        caplog.clear()
        parse_value(dict(d), "type", MonitorType)
        assert not caplog.records


class TestVersionCache:
    def _api(self, info):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
        api.timeout = 0.05
        api.wait_events = 5
        api._version = None
        api._event_data = {Event.INFO: info}
        return api

    def test_version_is_cached_and_does_not_sleep(self):
        api = self._api({"version": "2.5.6"})
        with mock.patch.object(api, "_get_event_data") as get, \
                mock.patch("time.sleep") as sleep:
            assert api.version == "2.5.6"
            api._event_data[Event.INFO] = {"version": "9.9.9"}
            assert api.version == "2.5.6"
        get.assert_not_called()
        sleep.assert_not_called()

    def test_new_info_event_resets_cache(self):
        api = self._api({"version": "2.5.6"})
        assert api.version == "2.5.6"
        api._event_info({"version": "2.6.0"})
        assert api.version == "2.6.0"

    def test_times_out_without_info(self):
        with pytest.raises(Timeout):
            _ = self._api(None).version


class TestSocketErrorMapping:
    def api(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api.sio = mock.Mock()
        api.timeout = 1
        api.url = "http://x"
        api.headers = None
        return api

    def test_call_maps_socketio_timeout(self):
        api = self.api()
        cause = socketio.exceptions.TimeoutError()
        api.sio.call.side_effect = cause
        with pytest.raises(Timeout) as cm:
            api._call("getMonitor", 1)
        assert cm.value.__cause__ is cause

    def test_call_maps_other_socketio_errors(self):
        for error in (socketio.exceptions.BadNamespaceError(),
                      socketio.exceptions.ConnectionError()):
            api = self.api()
            api.sio.call.side_effect = error
            with pytest.raises(UptimeKumaException) as cm:
                api._call("getMonitor", 1)
            assert not isinstance(cm.value, Timeout)
            assert cm.value.__cause__ is error

    def test_connect_raises_connection_error_with_cause(self):
        api = self.api()
        cause = socketio.exceptions.ConnectionError("refused")
        api.sio.connect.side_effect = cause
        with pytest.raises(UptimeKumaConnectionError) as cm:
            api.connect()
        assert cm.value.__cause__ is cause
        assert isinstance(cm.value, UptimeKumaException)

    def test_connect_does_not_swallow_keyboard_interrupt(self):
        api = self.api()
        api.sio.connect.side_effect = KeyboardInterrupt
        with pytest.raises(KeyboardInterrupt):
            api.connect()


class TestWaitForNewEvent:
    def _api(self, timeout=1):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
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
        assert time.time() - start >= 0.15
        assert api._event_data[Event.NOTIFICATION_LIST] == [{"id": 1}]

    def test_event_during_body_counts(self):
        api = self._api()
        with api.wait_for_event(Event.NOTIFICATION_LIST, new=True):
            api._event_notification_list([])

    def test_times_out_without_new_event(self):
        api = self._api(timeout=0.05)
        with pytest.raises(Timeout):
            with api.wait_for_event(Event.NOTIFICATION_LIST, new=True):
                pass

    def test_body_error_propagates_without_waiting(self):
        api = self._api(timeout=0.05)
        with pytest.raises(UptimeKumaException):
            with api.wait_for_event(Event.NOTIFICATION_LIST, new=True):
                raise UptimeKumaException("nope")

    def test_old_event_does_not_count_by_default(self):
        api = self._api(timeout=0.05)
        with api.wait_for_event(Event.NOTIFICATION_LIST):
            pass  # data already present, no new event needed


class TestEditMonitorShapes:
    """edit_monitor feeds get_monitor() output through the add_monitor path."""

    def edit(self, stored=None, **kwargs):
        monitor = dict(
            type=MonitorType.HTTP, name="m", interval=60, retryInterval=60,
            maxretries=0, url="http://x", maxredirects=10,
            accepted_statuscodes=["200-299"], dns_resolve_type="A",
            notificationIDList=[1, 2], databaseConnectionString=None,
            authMethod=AuthMethod.NONE, pushToken=None,
            kafkaProducerSaslOptions={"mechanism": "None"},
        )
        monitor.update(stored or {})
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
        api.wait_for_event = lambda *a, **k: contextlib.nullcontext()
        api.get_monitor = lambda id_: dict(monitor)
        with mock.patch.object(api, "_call", return_value={}) as call:
            api.edit_monitor(1, **kwargs)
        event, data = call.call_args.args
        assert event == "editMonitor"
        return data

    def test_edit_ntp_threshold_is_merged_and_validated(self):
        stored = dict(type=MonitorType.NTP, hostname="h", port=123,
                      ntpStratumThreshold=5, ntpTimeOffsetThreshold=1000,
                      ntpRootDispersionThreshold=500)
        data = self.edit(stored, ntpTimeOffsetThreshold=50)
        assert data["ntpTimeOffsetThreshold"] == 50
        assert data["ntpStratumThreshold"] == 5
        with pytest.raises(ValueError, match="ntpStratumThreshold"):
            self.edit(stored, ntpStratumThreshold=16)

    def test_edit_new_type_fields_are_merged_and_validated(self):
        smtp = dict(type=MonitorType.SMTP, hostname="h", port=465,
                    smtpSecurity="secure")
        data = self.edit(smtp, smtpSecurity="starttls")
        assert (data["smtpSecurity"], data["hostname"], data["port"]) == (
            "starttls", "h", 465)
        assert self.edit(smtp, smtpSecurity="nostarttls")["smtpSecurity"] \
            == "nostarttls"
        with pytest.raises(ValueError, match="smtpSecurity"):
            self.edit(smtp, smtpSecurity="tls")
        service = dict(type=MonitorType.PM2, system_service_name="a")
        assert self.edit(service, system_service_name="b")[
            "system_service_name"] == "b"
        manual = dict(type=MonitorType.MANUAL, manual_status=1)
        with pytest.raises(ValueError, match="manual_status"):
            self.edit(manual, manual_status=2)

    def test_edit_snmp_is_merged_and_validated(self):
        stored = dict(type=MonitorType.SNMP, hostname="h", port=161,
                      snmpOid="1.3", snmpVersion="2c", radiusPassword="public",
                      jsonPath="$", jsonPathOperator="==", expectedValue="1")
        data = self.edit(stored, jsonPathOperator=">", expectedValue="5")
        assert (data["jsonPathOperator"], data["expectedValue"]) == (">", "5")
        assert (data["snmpOid"], data["radiusPassword"], data["port"]) == (
            "1.3", "public", 161)
        with pytest.raises(ValueError, match="snmpVersion"):
            self.edit(stored, snmpVersion="3")

    def test_edit_snmp_name_only_with_missing_or_null_fields(self):
        stored = dict(type=MonitorType.SNMP, hostname="h", port=161,
                      snmpOid="1.3", radiusPassword="public",
                      expectedValue="1")
        assert self.edit(stored, name="x")["name"] == "x"
        nulls = dict(stored, snmpVersion=None, jsonPathOperator=None,
                     jsonPath=None)
        assert self.edit(nulls, name="x")["name"] == "x"

    def test_edit_sftp_is_merged_and_validated(self):
        stored = dict(type=MonitorType.SFTP, hostname="h", port=22,
                      sshUsername="u", sshAuthMethod="password",
                      sshPassword="pw", sshPrivateKey=None,
                      sshPassphrase=None, sftpPath=None)
        data = self.edit(stored, sftpPath="/x")
        assert (data["sftpPath"], data["sshPassword"], data["port"]) == (
            "/x", "pw", 22)
        with pytest.raises(TypeError, match="sshPrivateKey"):
            self.edit(stored, sshAuthMethod="privateKey")
        keyed = self.edit(stored, sshAuthMethod="privateKey",
                          sshPrivateKey="K")
        assert (keyed["sshPrivateKey"], keyed["sshAuthMethod"]) == (
            "K", "privateKey")

    def test_edit_sftp_private_key_monitor_keeps_its_secrets(self):
        stored = dict(type=MonitorType.SFTP, hostname="h", port=22,
                      sshUsername="u", sshAuthMethod="privateKey",
                      sshPrivateKey="K", sshPassphrase="pp",
                      sshPassword=None)
        data = self.edit(stored, name="x")
        assert (data["sshPrivateKey"], data["sshPassphrase"]) == ("K", "pp")
        back = self.edit(stored, sshAuthMethod="password", sshPassword="pw")
        assert (back["sshAuthMethod"], back["sshPassword"]) == (
            "password", "pw")

    def test_edit_globalping_is_merged_and_validated(self):
        stored = dict(type=MonitorType.GLOBALPING, subtype="ping",
                      hostname="h", port=80, location="world",
                      protocol="ICMP", ipFamily=None, ping_count=3)
        data = self.edit(stored, location="germany", ping_count=5)
        assert (data["location"], data["ping_count"], data["hostname"],
                data["subtype"]) == ("germany", 5, "h", "ping")
        with pytest.raises(ValueError, match="location"):
            self.edit(stored, location="a,b")
        with pytest.raises(ValueError, match="for subtype 'dns'"):
            self.edit(stored, subtype="dns", protocol="ICMP")

    def test_edit_globalping_switches_subtype_with_its_required_fields(self):
        stored = dict(type=MonitorType.GLOBALPING, subtype="ping",
                      hostname="h", port=80, location="world",
                      protocol="ICMP", ping_count=3, url=None)
        http = self.edit(stored, subtype="http", url="https://x",
                         protocol=None, method="GET")
        assert (http["subtype"], http["url"]) == ("http", "https://x")
        dns = self.edit(stored, subtype="dns", protocol="UDP")
        assert (dns["subtype"], dns["protocol"]) == ("dns", "UDP")
        with pytest.raises(TypeError, match="url"):
            self.edit(stored, subtype="http", protocol=None, method="GET")
        with pytest.raises(ValueError, match="ping_count"):
            self.edit(stored, ping_count=0)

    @pytest.mark.parametrize("subtype, protocol, port", [
        ("dns", "UDP", 53), ("ping", "ICMP", 80), ("http", None, None)])
    def test_edit_globalping_subtype_change_resets_port_and_protocol(
            self, subtype, protocol, port):
        other = "http" if subtype != "http" else "dns"
        stored = dict(type=MonitorType.GLOBALPING, subtype=other,
                      hostname="h", url="https://x", method="GET",
                      location="world", protocol="HTTP2", port=8080,
                      dns_resolve_type="A", ping_count=3)
        data = self.edit(stored, subtype=subtype)
        assert (data["protocol"], data["port"]) == (protocol, port)
        explicit = self.edit(stored, subtype=subtype, port=1234)
        assert explicit["port"] == 1234

    def test_edit_globalping_same_subtype_keeps_port_and_protocol(self):
        stored = dict(type=MonitorType.GLOBALPING, subtype="dns",
                      hostname="h", location="world", protocol="TCP",
                      port=5353, dns_resolve_type="A")
        data = self.edit(stored, subtype="dns", name="x")
        assert (data["protocol"], data["port"]) == ("TCP", 5353)

    def test_edit_globalping_http_with_bearer(self):
        stored = dict(type=MonitorType.GLOBALPING, subtype="http",
                      url="https://x", location="world", protocol=None,
                      method="GET", authMethod=AuthMethod.BEARER,
                      bearer_token="tok")
        assert self.edit(stored, name="x")["bearer_token"] == "tok"
        with pytest.raises(TypeError, match="bearer_token"):
            self.edit(dict(stored, bearer_token=None), name="x")

    def test_edit_sftp_stored_without_auth_method_is_password(self):
        stored = dict(type=MonitorType.SFTP, hostname="h", port=22,
                      sshUsername="u", sshAuthMethod=None, sshPassword="pw")
        assert self.edit(stored, name="x")["name"] == "x"
        no_pw = dict(stored, sshPassword=None)
        with pytest.raises(TypeError, match="sshPassword"):
            self.edit(no_pw, name="x")

    def test_edit_rabbitmq_is_merged_and_validated(self):
        stored = dict(type=MonitorType.RABBITMQ,
                      rabbitmqNodes=["http://a"], rabbitmqUsername="u",
                      rabbitmqPassword="pw")
        data = self.edit(stored, rabbitmqUsername="v")
        assert data["rabbitmqNodes"] == ["http://a"]
        assert (data["rabbitmqUsername"], data["rabbitmqPassword"]) == (
            "v", "pw")
        with pytest.raises(ValueError, match="rabbitmqNodes"):
            self.edit(stored, rabbitmqNodes=["a"])

    def test_edit_websocket_and_oracledb_fields_are_merged(self):
        ws = dict(type=MonitorType.WEBSOCKET_UPGRADE, url="ws://h",
                  accepted_statuscodes=["1000"], wsSubprotocol="a",
                  wsIgnoreSecWebsocketAcceptHeader=False)
        data = self.edit(ws, wsIgnoreSecWebsocketAcceptHeader=True)
        assert data["wsIgnoreSecWebsocketAcceptHeader"] is True
        assert (data["url"], data["wsSubprotocol"]) == ("ws://h", "a")
        db = dict(type=MonitorType.ORACLEDB, databaseConnectionString="c",
                  basic_auth_user="u", basic_auth_pass="p")
        data = self.edit(db, basic_auth_pass="q")
        assert (data["basic_auth_user"], data["basic_auth_pass"]) == ("u", "q")

    def test_edit_only_name_keeps_the_rest(self):
        data = self.edit(name="new")
        assert data["name"] == "new"
        assert data["url"] == "http://x"
        assert data["accepted_statuscodes"] == ["200-299"]
        assert data["notificationIDList"] == {1: True, 2: True}

    def test_notification_id_list_as_list(self):
        data = self.edit(notificationIDList=[3])
        assert data["notificationIDList"] == {3: True}

    def test_notification_id_list_as_dict(self):
        data = self.edit(notificationIDList={3: True})
        assert data["notificationIDList"] == {3: True}

    def test_empty_accepted_statuscodes_gets_default(self):
        for empty in ([], None):
            data = self.edit(accepted_statuscodes=empty)
            assert data["accepted_statuscodes"] == ["200-299"]

    def test_push_token_is_preserved(self):
        data = self.edit(stored=dict(type=MonitorType.PUSH, pushToken="tok"),
                         name="new")
        assert data["pushToken"] == "tok"

    def test_auth_method_is_preserved(self):
        data = self.edit(
            stored=dict(authMethod=AuthMethod.HTTP_BASIC), name="n"
        )
        assert data["authMethod"] == AuthMethod.HTTP_BASIC
        data = self.edit(authMethod=AuthMethod.NTLM)
        assert data["authMethod"] == AuthMethod.NTLM


class TestEventDataThreadSafety:
    def api(self):
        api = UptimeKumaApi.__new__(UptimeKumaApi)
        api._lock = threading.RLock()
        api.timeout = 5
        api.wait_events = 0
        api._event_data = {Event.HEARTBEAT_LIST: {}, Event.MONITOR_LIST: {}}
        api._event_seq = dict.fromkeys(api._event_data, 0)
        return api

    def blocked_while_locked(self, api, func):
        # runs func in a thread while another thread holds the lock: it must
        # not finish until the lock is released
        done = threading.Event()
        thread = threading.Thread(target=lambda: (func(), done.set()))
        with api._lock:
            thread.start()
            assert not done.wait(0.2)
        assert done.wait(2)
        thread.join()

    def test_handlers_take_the_lock(self):
        api = self.api()
        self.blocked_while_locked(api, lambda: api._event_heartbeat(
            {"monitorID": 1, "important": False, "id": 1}))
        self.blocked_while_locked(api, lambda: api._event_monitor_list({}))
        self.blocked_while_locked(
            api, lambda: api._event_update_monitor_into_list({"1": {}}))
        assert len(api._event_data[Event.HEARTBEAT_LIST][1]) == 1

    def test_cache_copy_takes_the_lock(self):
        api = self.api()
        self.blocked_while_locked(
            api, lambda: api._get_event_data(Event.HEARTBEAT_LIST))

    def test_status_page_cache_writes_take_the_lock(self):
        api = self.api()
        api._event_data[Event.STATUS_PAGE_LIST] = {"1": {"id": 1, "slug": "a"}}
        api._event_seq[Event.STATUS_PAGE_LIST] = 0
        api._call = lambda event, data=None: {"config": {"id": 2, "slug": "b"}}
        api.get_status_page = lambda slug: {"id": 2, "slug": slug}
        self.blocked_while_locked(api, lambda: api.save_status_page("b"))
        assert "2" in api._event_data[Event.STATUS_PAGE_LIST]
        api.get_status_pages = lambda: [{"slug": "a"}]
        self.blocked_while_locked(api, lambda: api.delete_status_page("a"))
        assert "1" not in api._event_data[Event.STATUS_PAGE_LIST]

    def test_concurrent_heartbeats_and_reads_stay_consistent(self):
        api = self.api()
        errors = []
        stop = threading.Event()

        def write(offset):
            try:
                for i in range(1000):
                    api._event_heartbeat(
                        {"monitorID": 1, "important": False, "id": offset + i})
            except Exception as e:
                errors.append(e)

        def read():
            try:
                while not stop.is_set():
                    beats = api._get_event_data(Event.HEARTBEAT_LIST).get(
                        1, []
                    )
                    assert len(beats) <= 150, len(beats)
                    time.sleep(0.001)
            except Exception as e:
                errors.append(e)

        writers = [
            threading.Thread(target=write, args=(n * 10000,)) for n in range(4)
        ]
        reader = threading.Thread(target=read)
        reader.start()
        for t in writers:
            t.start()
        for t in writers:
            t.join()
        stop.set()
        reader.join()
        assert errors == []
        assert len(api._event_data[Event.HEARTBEAT_LIST][1]) == 150
