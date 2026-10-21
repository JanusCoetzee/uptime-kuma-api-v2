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
                    "oauth_token_url", "ntpStratumThreshold"):
            assert key not in data

    def test_ntp_defaults_and_overrides(self):
        self.api.add_monitor(type=MonitorType.NTP, name="n", hostname="pool.ntp.org")
        self.api.add_monitor(type=MonitorType.NTP, name="n", hostname="h", port=124,
                             ntpStratumThreshold=3, ntpTimeOffsetThreshold=50,
                             ntpRootDispersionThreshold=20)
        first, second = self.api.sio.sent("add")
        assert first["type"] == MonitorType.NTP
        assert first["hostname"] == "pool.ntp.org"
        assert (first["ntpStratumThreshold"], first["ntpTimeOffsetThreshold"],
                first["ntpRootDispersionThreshold"]) == (5, 1000, 500)
        assert second["port"] == 124
        assert (second["ntpStratumThreshold"], second["ntpTimeOffsetThreshold"],
                second["ntpRootDispersionThreshold"]) == (3, 50, 20)

    @pytest.mark.parametrize("field, bad, good", [
        ("ntpStratumThreshold", 0, 1),
        ("ntpStratumThreshold", 16, 15),
        ("ntpTimeOffsetThreshold", 0, 1),
        ("ntpRootDispersionThreshold", 0, 1),
    ])
    def test_ntp_threshold_bounds(self, field, bad, good):
        with pytest.raises(ValueError, match=field):
            self.api.add_monitor(type=MonitorType.NTP, name="n", hostname="h", **{field: bad})
        self.api.add_monitor(type=MonitorType.NTP, name="n", hostname="h", **{field: good})

    @pytest.mark.parametrize("monitor_type", [
        MonitorType.SYSTEM_SERVICE, MonitorType.PM2])
    def test_service_name_types_send_the_name(self, monitor_type):
        self.api.add_monitor(type=monitor_type, name="n",
                             system_service_name="nginx")
        (data,) = self.api.sio.sent("add")
        assert data["system_service_name"] == "nginx"

    def test_sip_options_sends_host_and_port(self):
        self.api.add_monitor(type=MonitorType.SIP_OPTIONS, name="n",
                             hostname="sip.example", port=5060)
        (data,) = self.api.sio.sent("add")
        assert (data["hostname"], data["port"]) == ("sip.example", 5060)

    @pytest.mark.parametrize("name", ["", "  ", "\t"])
    @pytest.mark.parametrize("monitor_type", [
        MonitorType.SYSTEM_SERVICE, MonitorType.PM2])
    def test_blank_service_name_is_rejected(self, monitor_type, name):
        with pytest.raises(ValueError, match="^system_service_name must not be empty$"):
            self.api.add_monitor(type=monitor_type, name="n",
                                 system_service_name=name)
        assert self.api.sio.sent("add") == []

    @pytest.mark.parametrize("monitor_type", [
        MonitorType.SIP_OPTIONS, MonitorType.SMTP])
    @pytest.mark.parametrize("port, ok", [
        (0, True), (65535, True), (-1, False), (65536, False)])
    def test_port_bounds(self, monitor_type, port, ok):
        def add():
            self.api.add_monitor(type=monitor_type, name="n", hostname="h",
                                 port=port)
        if ok:
            add()
            assert self.api.sio.sent("add")[0]["port"] == port
        else:
            with pytest.raises(ValueError, match="port"):
                add()
            assert self.api.sio.sent("add") == []

    @pytest.mark.parametrize("security", ["secure", "starttls", "nostarttls"])
    def test_smtp_security_values_are_sent(self, security):
        self.api.add_monitor(type=MonitorType.SMTP, name="n", hostname="h",
                             port=25, smtpSecurity=security)
        (data,) = self.api.sio.sent("add")
        assert data["smtpSecurity"] == security

    def test_smtp_security_defaults_to_none(self):
        self.api.add_monitor(type=MonitorType.SMTP, name="n", hostname="h",
                             port=25)
        (data,) = self.api.sio.sent("add")
        assert data["smtpSecurity"] is None

    @pytest.mark.parametrize("security", ["tls", "SECURE", "", "ssl", 1])
    def test_smtp_security_rejects_other_values(self, security):
        with pytest.raises(ValueError, match="^Unknown smtpSecurity value: .*"
                           "expected 'secure', 'starttls' or 'nostarttls'$"):
            self.api.add_monitor(type=MonitorType.SMTP, name="n",
                                 hostname="h", port=25, smtpSecurity=security)
        assert self.api.sio.sent("add") == []

    @pytest.mark.parametrize("status", [0, 1, None])
    def test_manual_status_values_are_sent(self, status):
        self.api.add_monitor(type=MonitorType.MANUAL, name="n",
                             manual_status=status)
        (data,) = self.api.sio.sent("add")
        assert data["manual_status"] == status

    @pytest.mark.parametrize("status", [2, -1, "1", "up"])
    def test_manual_status_rejects_other_values(self, status):
        with pytest.raises(ValueError, match="manual_status"):
            self.api.add_monitor(type=MonitorType.MANUAL, name="n",
                                 manual_status=status)
        assert self.api.sio.sent("add") == []

    @pytest.mark.parametrize("kwargs", [
        {"smtpSecurity": "tls"}, {"manual_status": 2}])
    def test_other_types_do_not_validate_fields_they_do_not_send(self, kwargs):
        self.api.add_monitor(type=MonitorType.PORT, name="n", hostname="h",
                             port=1, **kwargs)
        (data,) = self.api.sio.sent("add")
        assert not set(kwargs) & set(data)

    def test_oracledb_sends_connection_login_and_query(self):
        self.api.add_monitor(
            type=MonitorType.ORACLEDB, name="n",
            databaseConnectionString="host:1521/XEPDB1",
            basic_auth_user="scott", basic_auth_pass="tiger",
            databaseQuery="SELECT 1 FROM DUAL")
        (data,) = self.api.sio.sent("add")
        assert data["databaseConnectionString"] == "host:1521/XEPDB1"
        assert (data["basic_auth_user"], data["basic_auth_pass"]) == (
            "scott", "tiger")
        assert data["databaseQuery"] == "SELECT 1 FROM DUAL"

    def test_websocket_upgrade_defaults_and_overrides(self):
        self.api.add_monitor(type=MonitorType.WEBSOCKET_UPGRADE, name="n",
                             url="wss://example.org/socket")
        self.api.add_monitor(type=MonitorType.WEBSOCKET_UPGRADE, name="n",
                             url="wss://example.org/socket",
                             wsSubprotocol="soap,mqtt",
                             wsIgnoreSecWebsocketAcceptHeader=True)
        first, second = self.api.sio.sent("add")
        assert first["url"] == "wss://example.org/socket"
        assert (first["wsSubprotocol"],
                first["wsIgnoreSecWebsocketAcceptHeader"]) == ("", False)
        assert (second["wsSubprotocol"],
                second["wsIgnoreSecWebsocketAcceptHeader"]) == (
                    "soap,mqtt", True)

    def test_websocket_upgrade_accepts_close_code_1000_by_default(self):
        self.api.add_monitor(type=MonitorType.WEBSOCKET_UPGRADE, name="n",
                             url="ws://h")
        self.api.add_monitor(type=MonitorType.HTTP, name="n", url="http://h")
        ws, http = self.api.sio.sent("add")
        assert ws["accepted_statuscodes"] == ["1000"]
        assert http["accepted_statuscodes"] == ["200-299"]

    @pytest.mark.parametrize("codes", [
        ["1000"], ["1000", "1001"], ["1000-1003"], ["4999"], ["1006-1006"]])
    def test_websocket_upgrade_close_codes_are_accepted(self, codes):
        self.api.add_monitor(type=MonitorType.WEBSOCKET_UPGRADE, name="n",
                             url="ws://h", accepted_statuscodes=codes)
        (data,) = self.api.sio.sent("add")
        assert data["accepted_statuscodes"] == codes

    @pytest.mark.parametrize("code", [
        "999", "5000", "200-299", "1003-1000", "1000-", "-1000", "abc", "",
        "1000-1001-1002", "\u0661\u0660\u0660\u0660", 1000])
    def test_websocket_upgrade_rejects_other_codes(self, code):
        with pytest.raises(ValueError, match="websocket close code"):
            self.api.add_monitor(type=MonitorType.WEBSOCKET_UPGRADE, name="n",
                                 url="ws://h", accepted_statuscodes=[code])
        assert self.api.sio.sent("add") == []

    def test_close_codes_are_not_http_status_codes(self):
        with pytest.raises(ValueError, match="accepted_statuscodes"):
            self.api.add_monitor(type=MonitorType.HTTP, name="n", url="u",
                                 accepted_statuscodes=["1000"])

    def test_timeout_default_is_5_for_snmp_and_48_otherwise(self):
        self.api.add_monitor(**self.SNMP)
        self.api.add_monitor(**self.SNMP, timeout=20)
        self.api.add_monitor(type=MonitorType.PORT, name="n", hostname="h",
                             port=1)
        snmp, snmp_set, port = self.api.sio.sent("add")
        assert (snmp["timeout"], snmp_set["timeout"], port["timeout"]) == (
            5, 20, 48)

    SNMP = dict(type=MonitorType.SNMP, name="n", hostname="h",
                snmpOid="1.3.6.1.2.1.1.3.0", radiusPassword="public",
                expectedValue="1")

    @pytest.mark.parametrize("monitor_type, port", [
        (MonitorType.DNS, 53), (MonitorType.RADIUS, 1812)])
    def test_snmp_port_default_is_not_applied_to_other_types(
            self, monitor_type, port):
        given = {MonitorType.DNS: dict(hostname="h",
                                       dns_resolve_server="1.1.1.1"),
                 MonitorType.RADIUS: dict(
                     radiusUsername="u", radiusPassword="p", radiusSecret="s",
                     radiusCalledStationId="c", radiusCallingStationId="d")}
        self.api.add_monitor(type=monitor_type, name="n", **given[monitor_type])
        (data,) = self.api.sio.sent("add")
        assert data["port"] == port

    def test_snmp_explicit_none_json_path_uses_the_default(self):
        self.api.add_monitor(**self.SNMP, jsonPath=None)
        (data,) = self.api.sio.sent("add")
        assert data["jsonPath"] == "$"

    def test_snmp_defaults(self):
        self.api.add_monitor(**self.SNMP)
        (data,) = self.api.sio.sent("add")
        assert data["port"] == 161
        assert (data["snmpVersion"], data["jsonPath"],
                data["jsonPathOperator"]) == ("2c", "$", "==")
        assert data["radiusPassword"] == "public"
        assert (data["snmpOid"], data["expectedValue"]) == (
            "1.3.6.1.2.1.1.3.0", "1")

    def test_snmp_overrides(self):
        self.api.add_monitor(**self.SNMP, port=1161, snmpVersion="1",
                             jsonPath="$.x", jsonPathOperator=">=")
        (data,) = self.api.sio.sent("add")
        assert (data["port"], data["snmpVersion"], data["jsonPath"],
                data["jsonPathOperator"]) == (1161, "1", "$.x", ">=")

    @pytest.mark.parametrize("missing", [
        "hostname", "snmpOid", "radiusPassword", "expectedValue"])
    def test_snmp_required_arguments(self, missing):
        kwargs = {k: v for k, v in self.SNMP.items() if k != missing}
        with pytest.raises(TypeError, match=missing):
            self.api.add_monitor(**kwargs)

    @pytest.mark.parametrize("version", ["3", "2", 2, "v2c", ""])
    def test_snmp_rejects_other_versions(self, version):
        with pytest.raises(ValueError, match="^Unknown snmpVersion value: .*, "
                           r"expected '1' or '2c' \(SNMPv3 is not supported "
                           r"by Kuma 2.5.6\)$"):
            self.api.add_monitor(**self.SNMP, snmpVersion=version)
        assert self.api.sio.sent("add") == []

    @pytest.mark.parametrize("operator", [
        ">", ">=", "<", "<=", "!=", "==", "contains"])
    def test_snmp_accepts_every_operator(self, operator):
        self.api.add_monitor(**self.SNMP, jsonPathOperator=operator)
        (data,) = self.api.sio.sent("add")
        assert data["jsonPathOperator"] == operator

    @pytest.mark.parametrize("operator", ["=", "<>", "CONTAINS", ""])
    def test_snmp_rejects_other_operators(self, operator):
        with pytest.raises(ValueError, match="^Unknown jsonPathOperator "
                           "value: .*expected '>', '>=', '<', '<=', '!=', "
                           "'==' or 'contains'$"):
            self.api.add_monitor(**self.SNMP, jsonPathOperator=operator)
        assert self.api.sio.sent("add") == []

    def test_new_type_fields_are_only_sent_for_their_type(self):
        self.api.add_monitor(type=MonitorType.PORT, name="n", hostname="h", port=1)
        (data,) = self.api.sio.sent("add")
        for key in ("system_service_name", "smtpSecurity", "manual_status",
                    "wsSubprotocol", "wsIgnoreSecWebsocketAcceptHeader",
                    "snmpOid", "snmpVersion", "jsonPathOperator"):
            assert key not in data

    @pytest.mark.parametrize("monitor_type, given, extra", [
        (MonitorType.SYSTEM_SERVICE, {"system_service_name": "nginx"},
         {"system_service_name"}),
        (MonitorType.PM2, {"system_service_name": "api"},
         {"system_service_name"}),
        (MonitorType.MANUAL, {"manual_status": 1}, {"manual_status"}),
        (MonitorType.SIP_OPTIONS, {"hostname": "h", "port": 5060}, set()),
        (MonitorType.SMTP, {"hostname": "h", "port": 25, "smtpSecurity": None},
         {"smtpSecurity"}),
        (MonitorType.SNMP,
         {k: v for k, v in SNMP.items() if k not in ("type", "name")},
         {"radiusPassword", "snmpOid", "snmpVersion", "jsonPath",
          "jsonPathOperator", "expectedValue"}),
        (MonitorType.MYSQL, {"databaseConnectionString": "c"},
         {"databaseQuery"}),
        (MonitorType.ORACLEDB, {"databaseConnectionString": "c"},
         {"basic_auth_user", "basic_auth_pass", "databaseQuery"}),
        (MonitorType.WEBSOCKET_UPGRADE, {"url": "ws://h"},
         {"wsSubprotocol", "wsIgnoreSecWebsocketAcceptHeader"}),
    ])
    def test_new_types_only_add_their_own_keys(self, monitor_type, given, extra):
        # compare against a type that sends no type specific fields
        self.api.add_monitor(type=MonitorType.GROUP, name="n")
        self.api.add_monitor(type=monitor_type, name="n", **given)
        base, data = self.api.sio.sent("add")
        base.pop("type")
        data.pop("type")
        assert set(data) - set(base) == extra
        assert set(base) <= set(data)

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
        (MonitorType.NTP, {}),
        (MonitorType.SYSTEM_SERVICE, {}),
        (MonitorType.PM2, {}),
        (MonitorType.SIP_OPTIONS, {}),
        (MonitorType.SIP_OPTIONS, {"hostname": "h"}),
        (MonitorType.SMTP, {}),
        (MonitorType.SMTP, {"hostname": "h"}),
        (MonitorType.ORACLEDB, {}),
        (MonitorType.WEBSOCKET_UPGRADE, {}),
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
