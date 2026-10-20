from __future__ import annotations

from urllib.parse import quote

import requests
from packaging.version import parse as parse_version

from .. import (
    Event,
    IncidentStyle,
    Timeout,
    UptimeKumaException
)
from .._helpers import (int_to_bool, parse_value)
from ._base import MixinBase


# status page
def parse_incident_style(data) -> None:
    parse_value(data, "style", IncidentStyle)


def _build_status_page_response(config, r2) -> dict:
    config.update(r2.get("config", {}))
    # Kuma 2.5+ returns a list under "incidents"; older versions a single "incident".
    # Keep "incident" (first one) for backwards compatibility.
    incidents = r2.get("incidents")
    if incidents is None:
        incidents = [r2["incident"]] if r2.get("incident") else []
    data = {
        **config,
        "incident": incidents[0] if incidents else None,
        "incidents": incidents,
        "publicGroupList": r2.get("publicGroupList", []),
        "maintenanceList": r2.get("maintenanceList", []),
    }
    parse_incident_style(incidents)
    # convert sendUrl from int to bool
    for i in data["publicGroupList"]:
        for j in i["monitorList"]:
            int_to_bool(j, ["sendUrl"])
    return data


class StatusPagesMixin(MixinBase):
    def _build_status_page_data(
            self,
            slug: str,

            # config
            id: int,
            title: str,
            description: str | None = None,
            theme: str | None = None,
            published: bool = True,
            showTags: bool = False,
            domainNameList: list | None = None,
            googleAnalyticsId: str | None = None,
            customCSS: str = "",
            footerText: str | None = None,
            showPoweredBy: bool = True,
            showCertificateExpiry: bool = False,

            icon: str = "/icon.svg",
            publicGroupList: list | None = None
    ) -> tuple[str, dict, str, list]:
        if not theme:
            if parse_version(self.version) >= parse_version("1.22"):
                theme = "auto"
            else:
                theme = "light"
        if theme not in ["auto", "light", "dark"]:
            raise ValueError(f"Unknown theme: {theme}. Valid themes: auto, light, dark")
        if not domainNameList:
            domainNameList = []
        if not publicGroupList:
            publicGroupList = []
        config = {
            "id": id,
            "slug": slug,
            "title": title,
            "description": description,
            "icon": icon,
            "theme": theme,
            "published": published,
            "showTags": showTags,
            "domainNameList": domainNameList,
            "googleAnalyticsId": googleAnalyticsId,
            "customCSS": customCSS,
            "footerText": footerText,
            "showPoweredBy": showPoweredBy,
        }
        if parse_version(self.version) >= parse_version("1.23"):
            config.update({
                "showCertificateExpiry": showCertificateExpiry,
            })
        return slug, config, icon, publicGroupList

    def get_status_pages(self) -> list[dict]:
        """
        Get all status pages.

        :return: All status pages.
        :rtype: list

        Example::

            >>> api.get_status_pages()
            [
                {
                    'customCSS': '',
                    'description': 'description 1',
                    'domainNameList': [],
                    'footerText': None,
                    'icon': '/icon.svg',
                    'googleAnalyticsId': '',
                    'id': 1,
                    'published': True,
                    'showPoweredBy': False,
                    'showTags': False,
                    'slug': 'slug1',
                    'theme': 'light',
                    'title': 'status page 1'
                }
            ]
        """
        return list(self._get_event_data(Event.STATUS_PAGE_LIST).values())

    def get_status_page(self, slug: str) -> dict:
        """
        Get a status page.

        :param str slug: Slug
        :return: The status page.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_status_page("slug1")
            {
                'customCSS': '',
                'description': 'description 1',
                'domainNameList': [],
                'footerText': None,
                'googleAnalyticsId': '',
                'icon': '/icon.svg',
                'id': 1,
                'incident': {
                    'content': 'content 1',
                    'createdDate': '2022-12-15 16:51:43',
                    'id': 1,
                    'lastUpdatedDate': None,
                    'pin': 1,
                    'style': <IncidentStyle.DANGER: 'danger'>,
                    'title': 'title 1'
                },
                'incidents': [<same as 'incident'>],
                'maintenanceList': [],
                'publicGroupList': [
                    {
                        'id': 1,
                        'monitorList': [
                            {
                                'id': 1,
                                'name': 'monitor 1',
                                'sendUrl': False,
                                'type': 'http'
                            }
                        ],
                        'name': 'Services',
                        'weight': 1
                    }
                ],
                'published': True,
                'showCertificateExpiry': False,
                'showPoweredBy': False,
                'showTags': False,
                'slug': 'slug1',
                'theme': 'light',
                'title': 'status page 1'
            }
        """
        r1 = self._call('getStatusPage', slug)
        try:
            r2 = requests.get(
                f"{self.url}/api/status-page/{quote(slug, safe='')}",
                timeout=self.timeout,
                verify=self.ssl_verify,
                headers=self.headers,
            ).json()
        except requests.exceptions.Timeout as e:
            raise Timeout(e) from e
        except (requests.exceptions.RequestException, ValueError) as e:
            raise UptimeKumaException(e) from e

        return _build_status_page_response(r1["config"], r2)

    def add_status_page(self, slug: str, title: str) -> dict:
        """
        Add a status page.

        :param str slug: Slug
        :param str title: Title
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_status_page("slug1", "status page 1")
            {
                'msg': 'OK!'
            }
        """
        with self.wait_for_event(Event.STATUS_PAGE_LIST):
            return self._call('addStatusPage', (title, slug))

    def delete_status_page(self, slug: str) -> dict:
        """
        Delete a status page.

        :param str slug: Slug
        :return: The server response.
        :rtype: dict

        Example::

            >>> api.delete_status_page("slug1")
            {}
        """
        with self.wait_for_event(Event.STATUS_PAGE_LIST):
            if slug not in [i["slug"] for i in self.get_status_pages()]:
                raise UptimeKumaException("status page does not exist")
            r = self._call('deleteStatusPage', slug)

            # uptime kuma does not send the status page list event when a status page is deleted
            with self._lock:
                for status_page in self._event_data[Event.STATUS_PAGE_LIST].values():
                    if status_page["slug"] == slug:
                        status_page_id = status_page["id"]
                        del self._event_data[Event.STATUS_PAGE_LIST][str(status_page_id)]
                        break

            return r

    def save_status_page(self, slug: str, **kwargs) -> dict:
        """
        Save a status page.

        :param str slug: Slug
        :param int id: Id of the status page to save
        :param str, optional title: Title, defaults to None
        :param str, optional description: Description, defaults to None
        :param str, optional theme: Switch Theme, defaults to "auto"
        :param bool, optional published: Published, defaults to True
        :param bool, optional showTags: Show Tags, defaults to False
        :param list, optional domainNameList: Domain Names, defaults to None
        :param str, optional googleAnalyticsId: Google Analytics ID, defaults to None
        :param str, optional customCSS: Custom CSS, defaults to ""
        :param str, optional footerText: Custom Footer, defaults to None
        :param bool, optional showPoweredBy: Show Powered By, defaults to True
        :param bool, optional showCertificateExpiry: Show Certificate Expiry, defaults to False
        :param str, optional icon: Icon, defaults to "/icon.svg"
        :param list, optional publicGroupList: Public Group List, defaults to None
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> monitor_id = 1
            >>> api.save_status_page(
            ...     slug="slug1",
            ...     title="status page 1",
            ...     description="description 1",
            ...     publicGroupList=[
            ...         {
            ...             'name': 'Services',
            ...             'weight': 1,
            ...             'monitorList': [
            ...                 {
            ...                     "id": monitor_id
            ...                 }
            ...             ]
            ...         }
            ...     ]
            ... )
            {
                'publicGroupList': [
                    {
                        'id': 1,
                        'monitorList': [
                            {
                                'id': 1
                            }
                        ],
                        'name': 'Services',
                        'weight': 1
                    }
                ]
            }
        """
        # Bypass _build_status_page_data and preserve the full config from
        # get_status_page. The builder strips the config down to a fixed set
        # of v1.x-era fields and rebuilds, but Kuma 2.x has more config
        # fields (analyticsType, analyticsId, analyticsScriptUrl,
        # autoRefreshInterval, showOnlyLastHeartbeat, rssTitle) that the
        # server validates on save — stripping them produces an
        # "Invalid analytics type" error from the server.
        #
        # Critically: do NOT coerce null fields to defaults. Overriding null
        # analyticsType to "none" produces the same "Invalid analytics type"
        # error. The server accepts whatever it returned; round-trip it.
        status_page = self.get_status_page(slug)
        public_group_list = status_page.pop("publicGroupList", [])
        status_page.pop("incident", None)
        status_page.pop("incidents", None)
        status_page.pop("maintenanceList", None)
        if "publicGroupList" in kwargs:
            public_group_list = kwargs.pop("publicGroupList")
        status_page.update(kwargs)
        icon = status_page.get("icon", "/icon.svg")
        data = (slug, status_page, icon, public_group_list)
        r = self._call('saveStatusPage', data)

        # uptime kuma does not send the status page list event when a status page is saved
        status_page = self._call('getStatusPage', slug)["config"]
        status_page_id = status_page["id"]
        with self._lock:
            if self._event_data[Event.STATUS_PAGE_LIST] is None:
                self._event_data[Event.STATUS_PAGE_LIST] = {}
            self._event_data[Event.STATUS_PAGE_LIST][str(status_page_id)] = status_page

        return r

    def post_incident(
            self,
            slug: str,
            title: str,
            content: str,
            style: IncidentStyle = IncidentStyle.PRIMARY
    ) -> dict:
        """
        Post an incident to status page.

        :param str slug: Slug
        :param str title: Title
        :param str content: Content
        :param IncidentStyle, optional style: Style, defaults to :attr:`~.IncidentStyle.PRIMARY`
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.post_incident(
            ...     slug="slug1",
            ...     title="title 1",
            ...     content="content 1",
            ...     style=IncidentStyle.DANGER
            ... )
            {
                'content': 'content 1',
                'createdDate': '2022-12-15 16:51:43',
                'id': 1,
                'pin': True,
                'style': <IncidentStyle.DANGER: 'danger'>,
                'title': 'title 1'
            }
        """
        incident = {
            "title": title,
            "content": content,
            "style": style
        }
        r = self._call('postIncident', (slug, incident))["incident"]
        self.save_status_page(slug)
        parse_incident_style(r)
        return r

    def unpin_incident(self, slug: str) -> dict:
        """
        Unpin an incident from a status page.

        :param str slug: Slug
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.unpin_incident(slug="slug1")
            {}
        """
        r = self._call('unpinIncident', slug)
        self.save_status_page(slug)
        return r
