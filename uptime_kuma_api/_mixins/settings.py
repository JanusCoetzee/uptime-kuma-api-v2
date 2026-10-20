from __future__ import annotations

from packaging.version import parse as parse_version
from ._base import MixinBase


def _merge_settings(current, overrides) -> dict:
    data = {**current, **{k: v for k, v in overrides.items() if v is not None}}
    # the server assigns data.entryPage unconditionally; unset settings are absent from getSettings
    data.setdefault("entryPage", "dashboard")
    return data


class SettingsMixin(MixinBase):
    def get_settings(self) -> dict:
        """
        Get settings.

        :return: Settings.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_settings()
            {
                'checkBeta': False,
                'checkUpdate': False,
                'chromeExecutable': '',
                'disableAuth': False,
                'dnsCache': True,
                'entryPage': 'dashboard',
                'keepDataPeriodDays': 180,
                'nscd': False,
                'primaryBaseURL': '',
                'searchEngineIndex': False,
                'serverTimezone': 'Europe/Berlin',
                'steamAPIKey': '',
                'tlsExpiryNotifyDays': [
                    7,
                    14,
                    21
                ],
                'trustProxy': False
            }
        """
        r = self._call('getSettings')["data"]
        return r

    def set_settings(
            self,
            password: str | None = None,  # only required if disableAuth is true

            # about
            checkUpdate: bool | None = None,
            checkBeta: bool | None = None,

            # monitor history
            keepDataPeriodDays: int | None = None,

            # general
            serverTimezone: str | None = None,
            entryPage: str | None = None,
            searchEngineIndex: bool | None = None,
            primaryBaseURL: str | None = None,
            steamAPIKey: str | None = None,
            nscd: bool | None = None,
            dnsCache: bool | None = None,
            chromeExecutable: str | None = None,

            # notifications
            tlsExpiryNotifyDays: list | None = None,

            # security
            disableAuth: bool | None = None,

            # reverse proxy
            trustProxy: bool | None = None
    ) -> dict:
        r"""
        Set settings. Only the arguments that are not ``None`` are changed; all other
        settings keep their current server value.

        :param str, optional password: Password, only required if disableAuth is enabled, defaults to None
        :param bool, optional checkUpdate: Show update if available, defaults to None (keep the current server value)
        :param bool, optional checkBeta: Also check beta release, defaults to None (keep the current server value)
        :param int, optional keepDataPeriodDays: Keep monitor history data for X days. Set to 0 for infinite retention., defaults to None (keep the current server value)
        :param str, optional serverTimezone: Server Timezone, defaults to None (keep the current server value)
        :param str, optional entryPage: Entry Page, defaults to None (keep the current server value)
        :param bool, optional searchEngineIndex: Search Engine Visibility, defaults to None (keep the current server value)
        :param str, optional primaryBaseURL: Primary Base URL, defaults to None (keep the current server value)
        :param str, optional steamAPIKey: Steam API Key. For monitoring a Steam Game Server you need a Steam Web-API key., defaults to None (keep the current server value)
        :param bool, optional nscd: Enable NSCD (Name Service Cache Daemon) for caching all DNS requests, defaults to None (keep the current server value)
        :param bool, optional dnsCache: True to enable DNS Cache. It may be not working in some IPv6 environments, disable it if you encounter any issues., defaults to None (keep the current server value)
        :param str, optional chromeExecutable: Chrome/Chromium Executable, defaults to None (keep the current server value)
        :param list, optional tlsExpiryNotifyDays: TLS Certificate Expiry. HTTPS Monitors trigger notification when TLS certificate expires in., defaults to None (keep the current server value)
        :param bool, optional disableAuth: Disable Authentication, defaults to None (keep the current server value)
        :param bool, optional trustProxy: Trust Proxy. Trust 'X-Forwarded-\*' headers. If you want to get the correct client IP and your Uptime Kuma is behind such as Nginx or Apache, you should enable this., defaults to None (keep the current server value)
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.set_settings(
            ...     checkUpdate=False,
            ...     checkBeta=False,
            ...     keepDataPeriodDays=180,
            ...     serverTimezone="Europe/Berlin",
            ...     entryPage="dashboard",
            ...     searchEngineIndex=False,
            ...     primaryBaseURL="",
            ...     steamAPIKey="",
            ...     dnsCache=False,
            ...     tlsExpiryNotifyDays=[
            ...         7,
            ...         14,
            ...         21
            ...     ],
            ...     disableAuth=False,
            ...     trustProxy=False
            ... )
            {
                'msg': 'Saved'
            }
        """

        overrides = {
            "checkUpdate": checkUpdate,
            "checkBeta": checkBeta,
            "keepDataPeriodDays": keepDataPeriodDays,
            "serverTimezone": serverTimezone,
            "entryPage": entryPage,
            "searchEngineIndex": searchEngineIndex,
            "primaryBaseURL": primaryBaseURL,
            "steamAPIKey": steamAPIKey,
            "dnsCache": dnsCache,
            "tlsExpiryNotifyDays": tlsExpiryNotifyDays,
            "disableAuth": disableAuth,
            "trustProxy": trustProxy,
        }
        if parse_version(self.version) >= parse_version("1.23"):
            overrides["chromeExecutable"] = chromeExecutable
        if parse_version(self.version) >= parse_version("1.23.1"):
            overrides["nscd"] = nscd
        data = _merge_settings(self.get_settings(), overrides)
        return self._call('setSettings', (data, password))

    def change_password(self, old_password: str, new_password: str) -> dict:
        """
        Change password.

        :param str old_password: Old password
        :param str new_password: New password
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.change_password(
            ...     old_password="secret123",
            ...     new_password="321terces"
            ... )
            {
                'msg': 'Password has been updated successfully.'
            }
        """
        return self._call('changePassword', {
            "currentPassword": old_password,
            "newPassword": new_password,
        })

    def upload_backup(self, json_data: str, import_handle: str = "skip") -> dict:
        """
        Import Backup.

        :param str json_data: Backup data as json string.
        :param str, optional import_handle: Choose "skip" if you want to skip every monitor or notification with the same name. "overwrite" will delete every existing monitor and notification. "keep" will keep both., defaults to "skip"
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> json_data = json.dumps({
            ...     "version": "1.17.1",
            ...     "notificationList": [],
            ...     "monitorList": [],
            ...     "proxyList": []
            ... })
            >>> api.upload_backup(
            ...     json_data=json_data,
            ...     import_handle="overwrite"
            ... )
            {
                'msg': 'Backup successfully restored.'
            }
        """
        if import_handle not in ["overwrite", "skip", "keep"]:
            raise ValueError(f"Unknown import_handle value: {import_handle}")
        return self._call('uploadBackup', (json_data, import_handle))

    def get_database_size(self) -> dict:
        """
        Get database size.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_database_size()
            {
                'size': 61440
            }
        """
        return self._call('getDatabaseSize')

    def shrink_database(self) -> dict:
        """
        Shrink database.

        Trigger database VACUUM for SQLite. If your database is created after 1.10.0, AUTO_VACUUM is already enabled and this action is not needed.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.shrink_database()
            {}
        """
        return self._call('shrinkDatabase')
