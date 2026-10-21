import unittest

from uptime_kuma_client import MonitorStatus
from uptime_kuma_test_case import UptimeKumaTestCase


class TestHelperMethods(UptimeKumaTestCase):
    def test_monitor_status(self):
        monitor_id = self.add_monitor()
        status = self.api.get_monitor_status(monitor_id)
        self.assertTrue(type(status) is MonitorStatus)


if __name__ == '__main__':
    unittest.main()
