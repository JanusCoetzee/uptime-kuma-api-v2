import unittest

from uptime_kuma_client import UptimeKumaException
from uptime_kuma_test_case import UptimeKumaTestCase


class TestServerChecks(UptimeKumaTestCase):
    def test_cert_info(self):
        # no monitor has a certificate yet
        self.assertEqual(self.api.cert_info(), {})

    def test_check_apprise(self):
        self.assertIsInstance(self.api.check_apprise(), bool)

    def test_test_chrome_rejects_a_missing_executable(self):
        with self.assertRaises(UptimeKumaException):
            self.api.test_chrome("/nonexistent/chrome")


if __name__ == '__main__':
    unittest.main()
