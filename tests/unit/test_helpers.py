import unittest

from uptime_kuma_api import (
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
    _check_missing_arguments,
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
        self.assertTrue(k["pushToken"])

    @unittest.expectedFailure  # placeholder connection strings are sent to the server (issue #11 area)
    def test_no_placeholder_connection_string(self):
        k = self.kwargs(type=MonitorType.POSTGRES)
        _convert_monitor_input(k)
        self.assertFalse(k["databaseConnectionString"])


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

    @unittest.expectedFailure  # KeyError for types the library does not know (#40)
    def test_unknown_type_raises_clean_error(self):
        with self.assertRaises((TypeError, ValueError)):
            _check_arguments_monitor(self.monitor(type="ntp"))

    def test_every_monitor_type_has_required_args_entry(self):
        for t in MonitorType:
            try:
                _check_arguments_monitor(self.monitor(type=t))
            except KeyError:
                self.fail(f"{t} missing from required_args_by_type")
            except (TypeError, ValueError):
                pass

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


if __name__ == "__main__":
    unittest.main()
