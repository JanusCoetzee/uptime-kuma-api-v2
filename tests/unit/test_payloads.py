"""Exact request payloads with their defaults.

These pin what is sent to the server, so changing a default, a key or a
condition shows up here (and in mutation testing).
"""
import datetime
import pytest

from tests.unit.fake_kuma import make_api
from uptime_kuma_api import (
    AuthMethod,
    Event,
    MaintenanceStrategy,
    MonitorType,
    ProxyProtocol,
    UptimeKumaApi,
)


class TestMonitorPayload:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.api = make_api()

    def test_http_defaults(self):
        self.api.add_monitor(type=MonitorType.HTTP, name="n", url="http://x")
        assert self.api.sio.sent("add") == [
            {
                "accepted_statuscodes": ["200-299"],
                "authMethod": AuthMethod.NONE,
                "body": None,
                "conditions": None,
                "databaseConnectionString": None,
                "description": None,
                "dns_resolve_server": "1.1.1.1",
                "dns_resolve_type": "A",
                "expiryNotification": False,
                "headers": None,
                "hostname": None,
                "httpBodyEncoding": "json",
                "ignoreTls": False,
                "interval": 60,
                "maxredirects": 10,
                "maxretries": 1,
                "method": "GET",
                "mqttPassword": "",
                "mqttSuccessMessage": "",
                "mqttTopic": "",
                "mqttUsername": "",
                "name": "n",
                "notificationIDList": {},
                "packetSize": 56,
                "parent": None,
                "port": None,
                "proxyId": None,
                "resendInterval": 0,
                "retryInterval": 60,
                "timeout": 48,
                "type": MonitorType.HTTP,
                "upsideDown": False,
                "url": "http://x",
            }
        ]

    def test_overrides_are_sent(self):
        self.api.add_monitor(
            type=MonitorType.HTTP, name="n", url="u", interval=30,
            retryInterval=20, resendInterval=3, maxretries=5,
            upsideDown=True, description="d", parent=4, method="POST",
            body="b", headers="h", ignoreTls=True, expiryNotification=True,
            proxyId=2, maxredirects=0, accepted_statuscodes=["300-399"],
            timeout=7, httpBodyEncoding="xml")
        (data,) = self.api.sio.sent("add")
        for key, value in {
                "interval": 30, "retryInterval": 20, "resendInterval": 3,
                "maxretries": 5, "upsideDown": True, "description": "d",
                "parent": 4, "method": "POST", "body": "b", "headers": "h",
                "ignoreTls": True, "expiryNotification": True, "proxyId": 2,
                "maxredirects": 0, "accepted_statuscodes": ["300-399"],
                "timeout": 7, "httpBodyEncoding": "xml"}.items():
            assert data[key] == value

    def test_type_specific_fields_are_only_sent_for_their_type(self):
        self.api.add_monitor(type=MonitorType.HTTP, name="n", url="u")
        (data,) = self.api.sio.sent("add")
        for key in ("keyword", "grpcUrl", "radiusSecret", "docker_host",
                    "game", "jsonPath", "kafkaProducerTopic",
                    "databaseQuery", "basic_auth_user", "tlsCert",
                    "oauth_token_url"):
            assert key not in data

    def test_basic_auth_fields_but_not_ntlm_ones(self):
        self.api.add_monitor(type=MonitorType.HTTP, name="n", url="u",
                             authMethod=AuthMethod.HTTP_BASIC,
                             basic_auth_user="u", basic_auth_pass="p")
        (data,) = self.api.sio.sent("add")
        assert (data["basic_auth_user"], data["basic_auth_pass"]) == ("u", "p")
        assert "authDomain" not in data
        assert "tlsCert" not in data


class TestMonitorValidation:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.api = make_api()

    def rejects(self, error, **kwargs):
        kwargs.setdefault("type", MonitorType.HTTP)
        kwargs.setdefault("name", "n")
        kwargs.setdefault("url", "u")
        with pytest.raises(error):
            self.api.add_monitor(**kwargs)
        assert self.api.sio.calls == []

    def test_numeric_bounds(self):
        self.rejects(ValueError, interval=19)
        self.rejects(ValueError, retryInterval=19)
        self.rejects(ValueError, maxretries=-1)
        self.rejects(ValueError, maxredirects=-1)
        self.rejects(ValueError, type=MonitorType.PORT, hostname="h",
                     port=65536)
        self.rejects(ValueError, type=MonitorType.PORT, hostname="h",
                     port=-1)

    def test_bounds_are_inclusive(self):
        self.api.add_monitor(type=MonitorType.HTTP, name="n", url="u",
                             interval=20, retryInterval=20, maxretries=0,
                             resendInterval=0, maxredirects=0)
        self.api.add_monitor(type=MonitorType.PORT, name="n", hostname="h",
                             port=65535)
        self.api.add_monitor(type=MonitorType.PORT, name="n", hostname="h",
                             port=0)
        assert len(self.api.sio.sent("add")) == 3

    @pytest.mark.parametrize("monitor_type, given", [
        (MonitorType.HTTP, {}),
        (MonitorType.PORT, {"hostname": "h"}),
        (MonitorType.PING, {}),
        (MonitorType.KEYWORD, {"url": "u"}),
        (MonitorType.DOCKER, {"docker_container": "c"}),
        (MonitorType.POSTGRES, {}),
        (MonitorType.JSON_QUERY, {"url": "u"}),
    ])
    def test_required_arguments_per_type(self, monitor_type, given):
        with pytest.raises(TypeError):
            self.api.add_monitor(type=monitor_type, name="n", **given)

    def test_invalid_statuscodes_and_dns_types(self):
        for code in ("99", "1000", "abc", "200-300"):
            self.rejects(ValueError, accepted_statuscodes=[code])
        for dns_type in ("a", "", "ANY"):
            self.rejects(ValueError, type=MonitorType.DNS, hostname="h",
                         dns_resolve_server="1.1.1.1",
                         dns_resolve_type=dns_type)
        self.api.add_monitor(type=MonitorType.HTTP, name="n", url="u",
                             accepted_statuscodes=["100-199", "599", "100"])


class TestMaintenancePayload:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.api = make_api()

    def test_defaults(self):
        self.api.add_maintenance(title="t",
                                 strategy=MaintenanceStrategy.MANUAL)
        today = datetime.date.today().strftime("%Y-%m-%d 00:00:00")
        assert self.api.sio.sent("addMaintenance") == [
            {
                "active": True,
                "cron": "30 3 * * *",
                "dateRange": [today],
                "daysOfMonth": [],
                "description": "",
                "durationMinutes": 60,
                "intervalDay": 1,
                "strategy": MaintenanceStrategy.MANUAL,
                "timeRange": [{"hours": 2, "minutes": 0}, {"hours": 3, "minutes": 0}],
                "timezoneOption": None,
                "title": "t",
                "weekdays": [],
            }
        ]

    def test_overrides(self):
        self.api.add_maintenance(
            title="t", strategy=MaintenanceStrategy.RECURRING_INTERVAL,
            active=False, description="d", dateRange=["a", "b"],
            intervalDay=3, weekdays=[1], daysOfMonth=[2],
            timeRange=[{"hours": 1, "minutes": 2}, {"hours": 3, "minutes": 4}],
            cron="* * * * *", durationMinutes=5, timezoneOption="UTC")
        (data,) = self.api.sio.sent("addMaintenance")
        assert data["dateRange"] == ["a", "b"]
        assert data["timeRange"][1] == {"hours": 3, "minutes": 4}
        assert (
            data["active"],
            data["description"],
            data["intervalDay"],
            data["weekdays"],
            data["daysOfMonth"],
            data["cron"],
            data["durationMinutes"],
            data["timezoneOption"],
        ) == (False, "d", 3, [1], [2], "* * * * *", 5, "UTC")

    def test_strategy_arguments_are_validated(self):
        with pytest.raises(ValueError):
            self.api.add_maintenance(
                title="t", strategy=MaintenanceStrategy.RECURRING_INTERVAL,
                intervalDay=0)
        with pytest.raises(ValueError):
            self.api.add_maintenance(
                title="t", strategy=MaintenanceStrategy.RECURRING_INTERVAL,
                intervalDay=3651)
        assert self.api.sio.calls == []


class TestOtherPayloads:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.api = make_api()

    def test_proxy_defaults(self):
        self.api.add_proxy(protocol=ProxyProtocol.HTTP, host="h", port=80)
        assert self.api.sio.sent("addProxy") == [
            (
                {
                    "active": True,
                    "applyExisting": False,
                    "auth": False,
                    "default": False,
                    "host": "h",
                    "password": None,
                    "port": 80,
                    "protocol": ProxyProtocol.HTTP,
                    "username": None,
                },
                None,
            )
        ]

    def test_proxy_with_auth(self):
        self.api.add_proxy(protocol=ProxyProtocol.SOCKS5, host="h", port=1,
                           auth=True, username="u", password="p",
                           active=False, default=True, applyExisting=True)
        ((data, _),) = self.api.sio.sent("addProxy")
        assert (
            data["auth"],
            data["username"],
            data["password"],
            data["active"],
            data["default"],
            data["applyExisting"],
        ) == (True, "u", "p", False, True, True)
        with pytest.raises(TypeError):
            self.api.add_proxy(protocol=ProxyProtocol.HTTP, host="h",
                               port=1, auth=True, username="u")

    def test_status_page_data_defaults_and_overrides(self):
        assert self.api._build_status_page_data("s", id=1, title="t") == (
            "s",
            {
                "customCSS": "",
                "description": None,
                "domainNameList": [],
                "footerText": None,
                "googleAnalyticsId": None,
                "icon": "/icon.svg",
                "id": 1,
                "published": True,
                "showCertificateExpiry": False,
                "showPoweredBy": True,
                "showTags": False,
                "slug": "s",
                "theme": "auto",
                "title": "t",
            },
            "/icon.svg",
            [],
        )
        slug, config, icon, groups = self.api._build_status_page_data(
            "s", id=2, title="t", description="d", theme="dark",
            published=False, showTags=True, domainNameList=["a"],
            googleAnalyticsId="g", customCSS="c", footerText="f",
            showPoweredBy=False, showCertificateExpiry=True, icon="/i",
            publicGroupList=[{"name": "g"}])
        assert (icon, groups) == ("/i", [{"name": "g"}])
        assert (
            config["description"],
            config["theme"],
            config["published"],
            config["showTags"],
            config["domainNameList"],
            config["googleAnalyticsId"],
            config["customCSS"],
            config["footerText"],
            config["showPoweredBy"],
            config["showCertificateExpiry"],
            config["id"],
        ) == ("d", "dark", False, True, ["a"], "g", "c", "f", False, True, 2)

    def test_set_settings_sends_only_given_values(self):
        sio = self.api.sio
        sio.replies["getSettings"] = {"ok": True, "data": {
            "checkUpdate": True, "serverTimezone": "UTC", "nscd": True}}
        self.api.set_settings(checkBeta=False)
        ((data, password),) = sio.sent("setSettings")
        assert data == {
            "checkUpdate": True,
            "checkBeta": False,
            "serverTimezone": "UTC",
            "nscd": True,
            "entryPage": "dashboard",
        }
        assert password is None

    @pytest.mark.parametrize("kwargs, absent", [
        ({"nscd": True}, "chromeExecutable"),
        ({"chromeExecutable": "c"}, "nscd"),
    ])
    def test_set_settings_forwards_each_option_alone(self, kwargs, absent):
        self.api.sio.replies["getSettings"] = {"ok": True, "data": {}}
        self.api.set_settings(**kwargs)
        ((data, _),) = self.api.sio.sent("setSettings")
        assert kwargs.items() <= data.items()
        assert absent not in data

    def test_set_settings_all_arguments(self):
        sio = self.api.sio
        sio.replies["getSettings"] = {"ok": True, "data": {}}
        values = dict(
            checkUpdate=False, checkBeta=True, keepDataPeriodDays=9,
            serverTimezone="Z", entryPage="p", searchEngineIndex=True,
            primaryBaseURL="u", steamAPIKey="k", dnsCache=True,
            tlsExpiryNotifyDays=[1], disableAuth=True, trustProxy=True,
            chromeExecutable="c", nscd=False)
        self.api.set_settings(password="pw", **values)
        ((data, password),) = sio.sent("setSettings")
        assert data == values
        assert password == "pw"


class TestConstructorDefaults:
    def test_documented_defaults(self):
        import inspect
        params = inspect.signature(UptimeKumaApi.__init__).parameters
        assert (
            {
                k: v.default
                for k, v in params.items()
                if k != "self" and v.default is not inspect.Parameter.empty
            }
        ) == {"timeout": 10, "headers": None, "ssl_verify": True, "wait_events": 0.2}

    @pytest.mark.parametrize("event", [
        Event.MONITOR_LIST, Event.NOTIFICATION_LIST, Event.PROXY_LIST,
        Event.STATUS_PAGE_LIST, Event.HEARTBEAT_LIST,
        Event.IMPORTANT_HEARTBEAT_LIST, Event.AVG_PING, Event.UPTIME,
        Event.CERT_INFO, Event.DOCKER_HOST_LIST, Event.AUTO_LOGIN,
        Event.MAINTENANCE_LIST, Event.API_KEY_LIST,
    ])
    def test_all_events_start_empty_with_a_counter(self, event):
        api = make_api()
        assert api._event_data[event] is None
        assert api._event_seq[event] == 0
        assert len(api._event_seq) == len(api._event_data)

    def test_every_event_is_registered_with_its_handler(self):
        api = make_api()
        handlers = {
            Event.CONNECT: api._event_connect,
            Event.DISCONNECT: api._event_disconnect,
            Event.MONITOR_LIST: api._event_monitor_list,
            Event.UPDATE_MONITOR_INTO_LIST:
                api._event_update_monitor_into_list,
            Event.DELETE_MONITOR_FROM_LIST:
                api._event_delete_monitor_from_list,
            Event.NOTIFICATION_LIST: api._event_notification_list,
            Event.PROXY_LIST: api._event_proxy_list,
            Event.STATUS_PAGE_LIST: api._event_status_page_list,
            Event.HEARTBEAT_LIST: api._event_heartbeat_list,
            Event.IMPORTANT_HEARTBEAT_LIST:
                api._event_important_heartbeat_list,
            Event.AVG_PING: api._event_avg_ping,
            Event.UPTIME: api._event_uptime,
            Event.HEARTBEAT: api._event_heartbeat,
            Event.INFO: api._event_info,
            Event.CERT_INFO: api._event_cert_info,
            Event.DOCKER_HOST_LIST: api._event_docker_host_list,
            Event.AUTO_LOGIN: api._event_auto_login,
            Event.INIT_SERVER_TIMEZONE: api._event_init_server_timezone,
            Event.MAINTENANCE_LIST: api._event_maintenance_list,
            Event.API_KEY_LIST: api._event_api_key_list,
        }
        assert api.sio.handlers == handlers

    def test_constructor_stores_its_arguments(self):
        api = make_api(timeout=3, wait_events=0.5, ssl_verify=False,
                       headers={"a": "b"})
        assert (api.timeout, api.wait_events, api.ssl_verify, api.headers) == (
            3,
            0.5,
            False,
            {"a": "b"},
        )
