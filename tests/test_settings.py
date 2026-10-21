import json
import unittest

from uptime_kuma_test_case import UptimeKumaTestCase


class TestSettings(UptimeKumaTestCase):
    def test_settings(self):
        expected_settings = {
            "checkUpdate": False,
            "checkBeta": False,
            "keepDataPeriodDays": 180,
            "entryPage": "dashboard",
            "searchEngineIndex": False,
            "primaryBaseURL": "",
            "steamAPIKey": "",
            "tlsExpiryNotifyDays": [7, 14, 21],
            "disableAuth": False,
            "trustProxy": False,
            "serverTimezone": "Europe/Berlin",
            "dnsCache": True,
            "domainExpiryNotifyDays": [7, 14, 21],
            "globalpingApiToken": "token 1"
        }

        # set settings
        r = self.api.set_settings(self.password, **expected_settings)
        self.assertEqual(r["msg"], "Saved.")

        # set settings without password
        r = self.api.set_settings(**expected_settings)
        self.assertEqual(r["msg"], "Saved.")

        # get settings
        settings = self.api.get_settings()
        self.compare(settings, expected_settings)

    def test_set_one_setting_keeps_the_others(self):
        self.api.set_settings(steamAPIKey="key 1", keepDataPeriodDays=90)
        self.api.set_settings(domainExpiryNotifyDays=[5])
        settings = self.api.get_settings()
        self.assertEqual(settings["steamAPIKey"], "key 1")
        self.assertEqual(settings["keepDataPeriodDays"], 90)
        self.assertEqual(settings["domainExpiryNotifyDays"], [5])

    def test_change_password(self):
        new_password = "321terces"

        # change password
        r = self.api.change_password(self.password, new_password)
        self.assertEqual(r["msg"], "successAuthChangePassword")

        # check login
        r = self.api.login(self.username, new_password)
        self.assertIn("token", r)

        # restore password
        r = self.api.change_password(new_password, self.password)
        self.assertEqual(r["msg"], "successAuthChangePassword")

    @unittest.skip("uploadBackup was removed in Uptime Kuma 2.x")
    def test_upload_backup(self):
        data = {
            "version": "1.17.1",
            "notificationList": [],
            "monitorList": [],
            "proxyList": []
        }
        data_str = json.dumps(data)
        r = self.api.upload_backup(data_str, "overwrite")
        self.assertEqual(r["msg"], "Backup successfully restored.")


if __name__ == '__main__':
    unittest.main()
