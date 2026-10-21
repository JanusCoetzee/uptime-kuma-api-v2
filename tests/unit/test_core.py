import threading
import time
from unittest import mock

import pytest
import socketio

from tests.unit.fake_kuma import make_api
from uptime_kuma_api import (
    Event,
    Timeout,
    UptimeKumaApi,
    UptimeKumaConnectionError,
    UptimeKumaException,
)


class TestConstruction:
    def test_url_is_stripped_and_connect_is_called(self):
        api = make_api(headers={"X-A": "1"})
        assert api.url == "http://kuma.test"
        assert api.sio.connected
        assert api.sio.connect_args == (
            "http://kuma.test/socket.io/",
            0.3,
            {"X-A": "1"},
        )

    def test_every_event_has_a_handler(self):
        api = make_api()
        for name in (Event.CONNECT, Event.DISCONNECT, Event.MONITOR_LIST,
                     Event.HEARTBEAT, Event.INFO, Event.API_KEY_LIST):
            assert name in api.sio.handlers

    def test_ssl_verify_is_passed_to_the_client(self):
        with mock.patch("uptime_kuma_api.api.socketio.Client") as client:
            UptimeKumaApi("http://kuma.test", ssl_verify=False)
        client.assert_called_once_with(ssl_verify=False)

    def test_connection_failure_is_wrapped(self):
        sio = make_api().sio
        sio.connect_error = OSError("refused")
        with mock.patch("uptime_kuma_api.api.socketio.Client",
                        return_value=sio):
            with pytest.raises(UptimeKumaConnectionError) as ctx:
                UptimeKumaApi("http://kuma.test")
        assert isinstance(ctx.value.__cause__, OSError)

    def test_context_manager_disconnects(self):
        api = make_api()
        with api as same:
            assert same is api
            assert api.sio.connected
        assert not api.sio.connected

    def test_noop_handlers(self):
        api = make_api()
        assert api._event_connect() is None
        assert api._event_disconnect() is None
        assert api._event_init_server_timezone() is None


class TestCall:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.api = make_api()

    def test_ok_flag_is_removed(self):
        self.api.sio.replies["x"] = {"ok": True, "msg": "hi"}
        assert self.api._call("x") == {"msg": "hi"}

    def test_not_ok_raises_with_the_message(self):
        self.api.sio.replies["x"] = {"ok": False, "msg": "nope"}
        with pytest.raises(UptimeKumaException, match="nope"):
            self.api._call("x")

    def test_non_dict_reply_is_returned_as_is(self):
        self.api.sio.replies["x"] = True
        assert self.api._call("x") is True

    def test_dict_without_ok_is_returned_as_is(self):
        self.api.sio.replies["x"] = {"data": 1}
        assert self.api._call("x") == {"data": 1}

    def test_socketio_timeout_is_mapped(self):
        self.api.sio.replies["x"] = socketio.exceptions.TimeoutError()
        with pytest.raises(Timeout):
            self.api._call("x")

    def test_socketio_error_is_mapped(self):
        self.api.sio.replies["x"] = socketio.exceptions.BadNamespaceError("n")
        with pytest.raises(UptimeKumaException) as ctx:
            self.api._call("x")
        assert not isinstance(ctx.value, Timeout)


class TestEventHandlers:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.api = make_api()
        self.data = self.api._event_data
        self.seq = self.api._event_seq

    def test_monitor_list_replaces_and_counts(self):
        self.api._event_monitor_list({"1": {"id": 1}})
        assert self.data[Event.MONITOR_LIST] == {"1": {"id": 1}}
        assert self.seq[Event.MONITOR_LIST] == 1

    def test_monitor_delta_merges(self):
        self.api._event_monitor_list({"1": {"id": 1}})
        self.api._event_update_monitor_into_list({"2": {"id": 2}})
        assert set(self.data[Event.MONITOR_LIST]) == {"1", "2"}
        assert self.seq[Event.MONITOR_LIST] == 2

    def test_monitor_delta_before_the_list_is_ignored(self):
        self.api._event_update_monitor_into_list({"2": {"id": 2}})
        assert self.data[Event.MONITOR_LIST] is None
        assert self.seq[Event.MONITOR_LIST] == 1

    def test_monitor_delete(self):
        self.api._event_monitor_list({"1": {"id": 1}, "2": {"id": 2}})
        self.api._event_delete_monitor_from_list(1)
        assert set(self.data[Event.MONITOR_LIST]) == {"2"}
        self.api._event_delete_monitor_from_list(99)  # unknown id is fine
        assert set(self.data[Event.MONITOR_LIST]) == {"2"}

    def test_monitor_delete_before_the_list_is_ignored(self):
        self.api._event_delete_monitor_from_list(1)
        assert self.data[Event.MONITOR_LIST] is None

    @pytest.mark.parametrize("handler, event", [
        ("_event_notification_list", Event.NOTIFICATION_LIST),
        ("_event_proxy_list", Event.PROXY_LIST),
        ("_event_status_page_list", Event.STATUS_PAGE_LIST),
        ("_event_docker_host_list", Event.DOCKER_HOST_LIST),
        ("_event_maintenance_list", Event.MAINTENANCE_LIST),
        ("_event_api_key_list", Event.API_KEY_LIST),
    ])
    def test_plain_list_events(self, handler, event):
        getattr(self.api, handler)([{"id": 7}])
        assert self.data[event] == [{"id": 7}]
        assert self.seq[event] == 1

    def test_heartbeat_list_overwrite_replaces(self):
        self.api._event_heartbeat_list("1", [{"a": 1}], False)
        self.api._event_heartbeat_list("1", [{"a": 3}], True)
        assert self.data[Event.HEARTBEAT_LIST][1] == [{"a": 3}]
        self.api._event_important_heartbeat_list("2", [{"a": 1}], False)
        self.api._event_important_heartbeat_list("2", [], True)
        assert self.data[Event.IMPORTANT_HEARTBEAT_LIST][2] == []

    # The server sends a list of beats; they are merged, not nested (#102).
    def test_heartbeat_list_extends_with_the_new_beats(self):
        self.api._event_heartbeat_list("1", [{"a": 1}], False)
        self.api._event_heartbeat_list("1", [{"a": 2}], False)
        assert self.data[Event.HEARTBEAT_LIST][1] == [{"a": 2}, {"a": 1}]
        assert all(
            isinstance(b, dict) for b in self.data[Event.HEARTBEAT_LIST][1]
        )

    def test_heartbeat_list_merge_keeps_the_150_newest(self):
        self.api._event_heartbeat_list("1", [{"n": i} for i in range(100)],
                                       False)
        self.api._event_heartbeat_list("1", [{"n": i} for i in range(100)],
                                       False)
        beats = self.data[Event.HEARTBEAT_LIST][1]
        assert len(beats) == 150
        assert beats[-1] == {"n": 99}

    def test_overlapping_batch_does_not_duplicate_beats(self):
        live = [{"time": "t1", "status": 1}, {"time": "t2", "status": 1}]
        self.api._event_heartbeat_list("1", live, False)
        batch = [{"id": 1, "time": "t1", "status": 1},
                 {"id": 2, "time": "t2", "status": 1}]
        self.api._event_heartbeat_list("1", batch, False)
        assert self.data[Event.HEARTBEAT_LIST][1] == batch

    def test_partly_overlapping_batch_keeps_the_other_cached_beats(self):
        self.api._event_heartbeat_list(
            "1", [{"time": "t2"}, {"time": "t3"}], False)
        self.api._event_heartbeat_list(
            "1", [{"id": 1, "time": "t1"}, {"id": 2, "time": "t2"}], False)
        assert self.data[Event.HEARTBEAT_LIST][1] == [
            {"id": 1, "time": "t1"}, {"id": 2, "time": "t2"},
            {"time": "t3"}]

    def test_beats_without_a_time_are_never_dropped(self):
        self.api._event_heartbeat_list("1", [{"a": 1}], False)
        self.api._event_heartbeat_list("1", [{"a": 1}], False)
        assert len(self.data[Event.HEARTBEAT_LIST][1]) == 2

    def test_overlapping_important_batch_does_not_duplicate_beats(self):
        self.api._event_important_heartbeat_list(
            "2", [{"time": "t1"}], False)
        self.api._event_important_heartbeat_list(
            "2", [{"id": 9, "time": "t1"}, {"id": 8, "time": "t0"}], False)
        assert self.data[Event.IMPORTANT_HEARTBEAT_LIST][2] == [
            {"id": 9, "time": "t1"}, {"id": 8, "time": "t0"}]

    def test_important_heartbeat_list_extends_with_the_new_beats(self):
        self.api._event_important_heartbeat_list("2", [{"a": 1}], False)
        self.api._event_important_heartbeat_list("2", [{"a": 2}], False)
        assert self.data[Event.IMPORTANT_HEARTBEAT_LIST][2] == [
            {"a": 2},
            {"a": 1},
        ]

    def test_avg_ping_and_uptime_are_keyed_by_int_id(self):
        self.api._event_avg_ping("3", 12)
        self.api._event_uptime("3", 24, 0.5)
        self.api._event_uptime("3", 720, 0.9)
        assert self.data[Event.AVG_PING] == {3: 12}
        assert self.data[Event.UPTIME] == {3: {24: 0.5, 720: 0.9}}

    def test_single_heartbeat_is_capped_at_150(self):
        for i in range(152):
            self.api._event_heartbeat({"monitorID": 1, "important": False,
                                       "n": i})
        beats = self.data[Event.HEARTBEAT_LIST][1]
        assert len(beats) == 150
        assert beats[0]["n"] == 2
        assert self.data[Event.IMPORTANT_HEARTBEAT_LIST] is None

    def test_important_heartbeat_is_prepended(self):
        self.api._event_heartbeat({"monitorID": 1, "important": True, "n": 1})
        self.api._event_heartbeat({"monitorID": 1, "important": True, "n": 2})
        assert [
            b["n"] for b in self.data[Event.IMPORTANT_HEARTBEAT_LIST][1]
        ] == [2, 1]

    def test_info_without_version_is_ignored(self):
        self.api._event_info({"primaryBaseURL": "x"})
        assert self.data[Event.INFO] == {"version": "2.5.6"}

    def test_info_with_version_resets_the_cached_version(self):
        assert self.api.version == "2.5.6"
        self.api._event_info({"version": "2.6.0"})
        assert self.api.version == "2.6.0"

    def test_cert_info_is_decoded(self):
        self.api._event_cert_info("4", '{"valid": true}')
        assert self.data[Event.CERT_INFO] == {4: {"valid": True}}

    def test_auto_login(self):
        self.api._event_auto_login()
        assert self.data[Event.AUTO_LOGIN]


class TestWaiting:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.api = make_api(timeout=0.6)
        self._timers = []
        yield
        for timer in self._timers:
            timer.cancel()
            timer.join()

    def _later(self, func, *args):
        timer = threading.Timer(0.03, func, args)
        self._timers.append(timer)
        timer.start()

    def test_wait_for_event_times_out(self):
        with pytest.raises(Timeout):
            with self.api.wait_for_event(Event.PROXY_LIST):
                pass

    def test_wait_for_event_new_times_out_without_an_update(self):
        self.api._event_data[Event.PROXY_LIST] = []
        with pytest.raises(Timeout):
            with self.api.wait_for_event(Event.PROXY_LIST, new=True):
                pass

    def test_wait_for_event_returns_when_the_event_arrives(self):
        self._later(self.api._event_proxy_list, [])
        with self.api.wait_for_event(Event.PROXY_LIST):
            pass
        assert self.api._event_data[Event.PROXY_LIST] == []

    def test_wait_for_event_new_returns_on_a_fresh_update(self):
        self.api._event_data[Event.PROXY_LIST] = []
        self._later(self.api._event_proxy_list, [1])
        with self.api.wait_for_event(Event.PROXY_LIST, new=True):
            pass

    def test_get_event_data_times_out(self):
        with pytest.raises(Timeout):
            self.api._get_event_data(Event.PROXY_LIST)

    def test_get_event_data_returns_a_copy(self):
        self.api._event_proxy_list([{"id": 1}])
        r = self.api._get_event_data(Event.PROXY_LIST)
        r[0]["id"] = 2
        assert self.api._event_data[Event.PROXY_LIST][0]["id"] == 1

    def test_get_event_data_waits_wait_events_after_arrival(self):
        self.api.wait_events = 0.1
        self.api._event_proxy_list([])
        start = time.time()
        self.api._get_event_data(Event.PROXY_LIST)
        assert time.time() - start >= 0.09

    @pytest.mark.parametrize("event", [
        Event.AVG_PING, Event.UPTIME, Event.HEARTBEAT_LIST,
        Event.IMPORTANT_HEARTBEAT_LIST, Event.CERT_INFO,
    ])
    def test_monitor_events_return_empty_without_monitors(self, event):
        self.api._event_monitor_list({})
        assert self.api._get_event_data(event) == []

    def test_version_times_out_without_info(self):
        self.api._event_data[Event.INFO] = None
        with pytest.raises(Timeout):
            _ = self.api.version

    def test_version_is_cached(self):
        assert self.api.version == "2.5.6"
        self.api._event_data[Event.INFO] = None
        assert self.api.version == "2.5.6"

    def test_version_does_not_cache_a_stale_info(self):
        # an INFO event lands after the reader has fetched the old INFO but
        # before it caches the version: the handler must run after the cache
        # write, so that the stale version is invalidated, not kept
        api = self.api
        events = []

        class RacingInfo(dict):
            def get(self, key, default=None):
                event = threading.Thread(
                    target=api._event_info, args=({"version": "2.6.0"},))
                event.start()
                events.append(event)
                event.join(0.2)  # returns at once only if nothing blocks it
                return super().get(key, default)

        api._version = None
        api._event_data[Event.INFO] = RacingInfo(version="2.5.6")
        assert api.version == "2.5.6"
        events[0].join(5)
        assert api._version is None
        assert api.version == "2.6.0"
