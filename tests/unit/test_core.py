import threading
import time
import unittest
from unittest import mock

import socketio

from tests.unit.fake_kuma import make_api
from uptime_kuma_api import (
    Event,
    Timeout,
    UptimeKumaApi,
    UptimeKumaConnectionError,
    UptimeKumaException,
)


class TestConstruction(unittest.TestCase):
    def test_url_is_stripped_and_connect_is_called(self):
        api = make_api(headers={"X-A": "1"})
        self.assertEqual(api.url, "http://kuma.test")
        self.assertTrue(api.sio.connected)
        self.assertEqual(api.sio.connect_args,
                         ("http://kuma.test/socket.io/", 0.3, {"X-A": "1"}))

    def test_every_event_has_a_handler(self):
        api = make_api()
        for name in (Event.CONNECT, Event.DISCONNECT, Event.MONITOR_LIST,
                     Event.HEARTBEAT, Event.INFO, Event.API_KEY_LIST):
            self.assertIn(name, api.sio.handlers)

    def test_ssl_verify_is_passed_to_the_client(self):
        with mock.patch("uptime_kuma_api.api.socketio.Client") as client:
            UptimeKumaApi("http://kuma.test", ssl_verify=False)
        client.assert_called_once_with(ssl_verify=False)

    def test_connection_failure_is_wrapped(self):
        sio = make_api().sio
        sio.connect_error = OSError("refused")
        with mock.patch("uptime_kuma_api.api.socketio.Client",
                        return_value=sio):
            with self.assertRaises(UptimeKumaConnectionError) as ctx:
                UptimeKumaApi("http://kuma.test")
        self.assertIsInstance(ctx.exception.__cause__, OSError)

    def test_context_manager_disconnects(self):
        api = make_api()
        with api as same:
            self.assertIs(same, api)
            self.assertTrue(api.sio.connected)
        self.assertFalse(api.sio.connected)

    def test_noop_handlers(self):
        api = make_api()
        self.assertIsNone(api._event_connect())
        self.assertIsNone(api._event_disconnect())
        self.assertIsNone(api._event_init_server_timezone())


class TestCall(unittest.TestCase):
    def setUp(self):
        self.api = make_api()

    def test_ok_flag_is_removed(self):
        self.api.sio.replies["x"] = {"ok": True, "msg": "hi"}
        self.assertEqual(self.api._call("x"), {"msg": "hi"})

    def test_not_ok_raises_with_the_message(self):
        self.api.sio.replies["x"] = {"ok": False, "msg": "nope"}
        with self.assertRaisesRegex(UptimeKumaException, "nope"):
            self.api._call("x")

    def test_non_dict_reply_is_returned_as_is(self):
        self.api.sio.replies["x"] = True
        self.assertIs(self.api._call("x"), True)

    def test_dict_without_ok_is_returned_as_is(self):
        self.api.sio.replies["x"] = {"data": 1}
        self.assertEqual(self.api._call("x"), {"data": 1})

    def test_socketio_timeout_is_mapped(self):
        self.api.sio.replies["x"] = socketio.exceptions.TimeoutError()
        with self.assertRaises(Timeout):
            self.api._call("x")

    def test_socketio_error_is_mapped(self):
        self.api.sio.replies["x"] = socketio.exceptions.BadNamespaceError("n")
        with self.assertRaises(UptimeKumaException) as ctx:
            self.api._call("x")
        self.assertNotIsInstance(ctx.exception, Timeout)


class TestEventHandlers(unittest.TestCase):
    def setUp(self):
        self.api = make_api()
        self.data = self.api._event_data
        self.seq = self.api._event_seq

    def test_monitor_list_replaces_and_counts(self):
        self.api._event_monitor_list({"1": {"id": 1}})
        self.assertEqual(self.data[Event.MONITOR_LIST], {"1": {"id": 1}})
        self.assertEqual(self.seq[Event.MONITOR_LIST], 1)

    def test_monitor_delta_merges(self):
        self.api._event_monitor_list({"1": {"id": 1}})
        self.api._event_update_monitor_into_list({"2": {"id": 2}})
        self.assertEqual(set(self.data[Event.MONITOR_LIST]), {"1", "2"})
        self.assertEqual(self.seq[Event.MONITOR_LIST], 2)

    def test_monitor_delta_before_the_list_is_ignored(self):
        self.api._event_update_monitor_into_list({"2": {"id": 2}})
        self.assertIsNone(self.data[Event.MONITOR_LIST])
        self.assertEqual(self.seq[Event.MONITOR_LIST], 1)

    def test_monitor_delete(self):
        self.api._event_monitor_list({"1": {"id": 1}, "2": {"id": 2}})
        self.api._event_delete_monitor_from_list(1)
        self.assertEqual(set(self.data[Event.MONITOR_LIST]), {"2"})
        self.api._event_delete_monitor_from_list(99)  # unknown id is fine
        self.assertEqual(set(self.data[Event.MONITOR_LIST]), {"2"})

    def test_monitor_delete_before_the_list_is_ignored(self):
        self.api._event_delete_monitor_from_list(1)
        self.assertIsNone(self.data[Event.MONITOR_LIST])

    def test_plain_list_events(self):
        cases = [
            (self.api._event_notification_list, Event.NOTIFICATION_LIST),
            (self.api._event_proxy_list, Event.PROXY_LIST),
            (self.api._event_status_page_list, Event.STATUS_PAGE_LIST),
            (self.api._event_docker_host_list, Event.DOCKER_HOST_LIST),
            (self.api._event_maintenance_list, Event.MAINTENANCE_LIST),
            (self.api._event_api_key_list, Event.API_KEY_LIST),
        ]
        for handler, event in cases:
            with self.subTest(event=event):
                handler([{"id": 7}])
                self.assertEqual(self.data[event], [{"id": 7}])
                self.assertEqual(self.seq[event], 1)

    def test_heartbeat_list_appends_unless_overwrite(self):
        self.api._event_heartbeat_list("1", [{"a": 1}], False)
        self.api._event_heartbeat_list("1", {"a": 2}, False)
        self.assertEqual(self.data[Event.HEARTBEAT_LIST][1],
                         [{"a": 1}, {"a": 2}])
        self.api._event_heartbeat_list("1", [{"a": 3}], True)
        self.assertEqual(self.data[Event.HEARTBEAT_LIST][1], [{"a": 3}])

    def test_important_heartbeat_list_appends_unless_overwrite(self):
        self.api._event_important_heartbeat_list("2", [{"a": 1}], False)
        self.api._event_important_heartbeat_list("2", {"a": 2}, False)
        self.assertEqual(self.data[Event.IMPORTANT_HEARTBEAT_LIST][2],
                         [{"a": 1}, {"a": 2}])
        self.api._event_important_heartbeat_list("2", [], True)
        self.assertEqual(self.data[Event.IMPORTANT_HEARTBEAT_LIST][2], [])

    def test_avg_ping_and_uptime_are_keyed_by_int_id(self):
        self.api._event_avg_ping("3", 12)
        self.api._event_uptime("3", 24, 0.5)
        self.api._event_uptime("3", 720, 0.9)
        self.assertEqual(self.data[Event.AVG_PING], {3: 12})
        self.assertEqual(self.data[Event.UPTIME], {3: {24: 0.5, 720: 0.9}})

    def test_single_heartbeat_is_capped_at_150(self):
        for i in range(152):
            self.api._event_heartbeat({"monitorID": 1, "important": False,
                                       "n": i})
        beats = self.data[Event.HEARTBEAT_LIST][1]
        self.assertEqual(len(beats), 150)
        self.assertEqual(beats[0]["n"], 2)
        self.assertIsNone(self.data[Event.IMPORTANT_HEARTBEAT_LIST])

    def test_important_heartbeat_is_prepended(self):
        self.api._event_heartbeat({"monitorID": 1, "important": True, "n": 1})
        self.api._event_heartbeat({"monitorID": 1, "important": True, "n": 2})
        self.assertEqual(
            [b["n"] for b in self.data[Event.IMPORTANT_HEARTBEAT_LIST][1]],
            [2, 1])

    def test_info_without_version_is_ignored(self):
        self.api._event_info({"primaryBaseURL": "x"})
        self.assertEqual(self.data[Event.INFO], {"version": "2.5.6"})

    def test_info_with_version_resets_the_cached_version(self):
        self.assertEqual(self.api.version, "2.5.6")
        self.api._event_info({"version": "2.6.0"})
        self.assertEqual(self.api.version, "2.6.0")

    def test_cert_info_is_decoded(self):
        self.api._event_cert_info("4", '{"valid": true}')
        self.assertEqual(self.data[Event.CERT_INFO], {4: {"valid": True}})

    def test_auto_login(self):
        self.api._event_auto_login()
        self.assertTrue(self.data[Event.AUTO_LOGIN])


class TestWaiting(unittest.TestCase):
    def setUp(self):
        self.api = make_api(timeout=0.15)

    def test_wait_for_event_times_out(self):
        with self.assertRaises(Timeout):
            with self.api.wait_for_event(Event.PROXY_LIST):
                pass

    def test_wait_for_event_new_times_out_without_an_update(self):
        self.api._event_data[Event.PROXY_LIST] = []
        with self.assertRaises(Timeout):
            with self.api.wait_for_event(Event.PROXY_LIST, new=True):
                pass

    def test_wait_for_event_returns_when_the_event_arrives(self):
        threading.Timer(0.03, self.api._event_proxy_list, [[]]).start()
        with self.api.wait_for_event(Event.PROXY_LIST):
            pass
        self.assertEqual(self.api._event_data[Event.PROXY_LIST], [])

    def test_wait_for_event_new_returns_on_a_fresh_update(self):
        self.api._event_data[Event.PROXY_LIST] = []
        threading.Timer(0.03, self.api._event_proxy_list, [[1]]).start()
        with self.api.wait_for_event(Event.PROXY_LIST, new=True):
            pass

    def test_get_event_data_times_out(self):
        with self.assertRaises(Timeout):
            self.api._get_event_data(Event.PROXY_LIST)

    def test_get_event_data_returns_a_copy(self):
        self.api._event_proxy_list([{"id": 1}])
        r = self.api._get_event_data(Event.PROXY_LIST)
        r[0]["id"] = 2
        self.assertEqual(self.api._event_data[Event.PROXY_LIST][0]["id"], 1)

    def test_get_event_data_waits_wait_events_after_arrival(self):
        self.api.wait_events = 0.1
        self.api._event_proxy_list([])
        start = time.time()
        self.api._get_event_data(Event.PROXY_LIST)
        self.assertGreaterEqual(time.time() - start, 0.09)

    def test_monitor_events_return_empty_without_monitors(self):
        self.api._event_monitor_list({})
        for event in (Event.AVG_PING, Event.UPTIME, Event.HEARTBEAT_LIST,
                      Event.IMPORTANT_HEARTBEAT_LIST, Event.CERT_INFO):
            with self.subTest(event=event):
                self.assertEqual(self.api._get_event_data(event), [])

    def test_version_times_out_without_info(self):
        self.api._event_data[Event.INFO] = None
        with self.assertRaises(Timeout):
            _ = self.api.version

    def test_version_is_cached(self):
        self.assertEqual(self.api.version, "2.5.6")
        self.api._event_data[Event.INFO] = None
        self.assertEqual(self.api.version, "2.5.6")


if __name__ == "__main__":
    unittest.main()
