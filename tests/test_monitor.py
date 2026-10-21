import time
import unittest

from uptime_kuma_api import (
    UptimeKumaException,
    MonitorType,
    AuthMethod,
    MonitorStatus,
)
from uptime_kuma_test_case import UptimeKumaTestCase


class TestMonitor(UptimeKumaTestCase):
    def test_monitor(self):
        # get empty list to make sure that future accesses will also work
        self.api.get_monitors()

        notification_id_1 = self.add_notification()
        notification_id_2 = self.add_notification()

        expected_monitor = {
            "type": MonitorType.HTTP,
            "name": "monitor 1",
            "interval": 60,
            "retryInterval": 60,
            "maxretries": 0,
            "notificationIDList": [notification_id_1, notification_id_2],
            "upsideDown": False,
            "url": "http://127.0.0.1",
            "resendInterval": 0
        }

        # add monitor
        r = self.api.add_monitor(**expected_monitor)
        self.assertEqual(r["msg"], "successAdded")
        monitor_id = r["monitorID"]

        # get monitor
        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)

        # get monitors
        monitors = self.api.get_monitors()
        self.assertTrue(type(monitors[0]["type"]) is MonitorType)
        self.assertTrue(type(monitors[0]["authMethod"]) is AuthMethod)
        monitor = self.find_by_id(monitors, monitor_id)
        self.assertTrue(type(monitor["type"]) is MonitorType)
        self.assertTrue(type(monitor["authMethod"]) is AuthMethod)
        self.assertIsNotNone(monitor)
        self.compare(monitor, expected_monitor)

        # edit monitor
        expected_monitor["type"] = MonitorType.PING
        expected_monitor["name"] = "monitor 1 new"
        expected_monitor["hostname"] = "127.0.0.10"
        del expected_monitor["url"]
        r = self.api.edit_monitor(monitor_id, **expected_monitor)
        self.assertEqual(r["msg"], "Saved.")
        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)

        # pause monitor
        r = self.api.pause_monitor(monitor_id)
        self.assertEqual(r["msg"], "successPaused")

        # resume monitor
        r = self.api.resume_monitor(monitor_id)
        self.assertEqual(r["msg"], "successResumed")

        # get monitor beats
        r = self.api.get_monitor_beats(monitor_id, 6)
        self.assertTrue(type(r[0]["status"]) is MonitorStatus)

        # delete monitor
        r = self.api.delete_monitor(monitor_id)
        self.assertEqual(r["msg"], "successDeleted")
        with self.assertRaises(UptimeKumaException):
            self.api.get_monitor(monitor_id)

    def do_test_monitor_type(self, expected_monitor):
        r = self.api.add_monitor(**expected_monitor)
        self.assertEqual(r["msg"], "successAdded")
        monitor_id = r["monitorID"]

        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)

        expected_monitor.update({
            "name": "monitor 2"
        })
        r = self.api.edit_monitor(monitor_id, **expected_monitor)
        self.assertEqual(r["msg"], "Saved.")
        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)

        monitor = self.api.get_monitor(monitor_id)
        self.compare(monitor, expected_monitor)
        return monitor

    def test_edit_monitor_partial_kwargs(self):
        notification_id_1 = self.add_notification()
        notification_id_2 = self.add_notification()
        monitor_id = self.api.add_monitor(
            type=MonitorType.HTTP, name="monitor 1", url="http://127.0.0.1",
            accepted_statuscodes=["200-299", "300-399"],
            notificationIDList=[notification_id_1],
        )["monitorID"]

        # only the name: everything else is kept
        self.api.edit_monitor(monitor_id, name="monitor 2")
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(monitor["name"], "monitor 2")
        self.assertEqual(monitor["url"], "http://127.0.0.1")
        self.assertEqual(
            monitor["accepted_statuscodes"], ["200-299", "300-399"]
        )
        self.assertEqual(monitor["notificationIDList"], [notification_id_1])

        # notifications as a list
        self.api.edit_monitor(
            monitor_id, notificationIDList=[notification_id_2]
        )
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(monitor["notificationIDList"], [notification_id_2])

        # an empty list falls back to the default status codes
        self.api.edit_monitor(monitor_id, accepted_statuscodes=[])
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(monitor["accepted_statuscodes"], ["200-299"])

    def test_edit_monitor_keeps_push_token(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.PUSH, name="monitor 1")["monitorID"]
        token = self.api.get_monitor(monitor_id)["pushToken"]
        self.assertTrue(token)
        self.api.edit_monitor(monitor_id, name="monitor 2")
        self.assertEqual(self.api.get_monitor(monitor_id)["pushToken"], token)

    def test_edit_monitor_keeps_auth_method(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.HTTP, name="monitor 1", url="http://127.0.0.1",
            authMethod=AuthMethod.HTTP_BASIC,
            basic_auth_user="user", basic_auth_pass="pass",
        )["monitorID"]
        self.api.edit_monitor(monitor_id, name="monitor 2")
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(monitor["authMethod"], AuthMethod.HTTP_BASIC)
        self.assertEqual(monitor["basic_auth_user"], "user")

    def test_monitor_type_http(self):
        proxy_id = self.add_proxy()

        json_data = '{"key": "value"}'
        expected_monitor = {
            "type": MonitorType.HTTP,
            "name": "monitor 1",
            "url": "http://127.0.0.1",
            "expiryNotification": False,
            "ignoreTls": False,
            "maxredirects": 10,
            "accepted_statuscodes": ["200-299"],
            "proxyId": proxy_id,
            "method": "GET",
            "body": json_data,
            "headers": json_data,
            "authMethod": AuthMethod.NONE
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_auth_method(self):
        for auth_method in [AuthMethod.HTTP_BASIC, AuthMethod.NTLM]:
            expected_monitor = {
                "type": MonitorType.HTTP,
                "name": "monitor 1",
                "url": "http://127.0.0.1",
                "authMethod": auth_method,
                "basic_auth_user": "auth user",
                "basic_auth_pass": "auth pass",
            }
            self.do_test_monitor_type(expected_monitor)

        expected_monitor = {
            "type": MonitorType.HTTP,
            "name": "monitor 1",
            "url": "http://127.0.0.1",
            "authMethod": AuthMethod.NTLM,
            "authDomain": "auth domain",
            "authWorkstation": "auth workstation",
        }
        self.do_test_monitor_type(expected_monitor)

        expected_monitor = {
            "type": MonitorType.HTTP,
            "name": "monitor 1",
            "url": "http://127.0.0.1",
            "authMethod": AuthMethod.MTLS,
            "tlsCert": "cert",
            "tlsKey": "key",
            "tlsCa": "ca",
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_port(self):
        expected_monitor = {
            "type": MonitorType.PORT,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "port": 8888
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_ping(self):
        expected_monitor = {
            "type": MonitorType.PING,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "packetSize": 56
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_keyword(self):
        expected_monitor = {
            "type": MonitorType.KEYWORD,
            "name": "monitor 1",
            "url": "http://127.0.0.1",
            "keyword": "healthy"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_grpc_keyword(self):
        expected_monitor = {
            "type": MonitorType.GRPC_KEYWORD,
            "name": "monitor 1",
            "grpcUrl": "127.0.0.1",
            "keyword": "healthy",
            "grpcServiceName": "health",
            "grpcMethod": "check",
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_dns(self):
        expected_monitor = {
            "type": MonitorType.DNS,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "port": 8888,
            "dns_resolve_server": "1.1.1.1",
            "dns_resolve_type": "A"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_docker(self):
        docker_host_id = self.add_docker_host()
        expected_monitor = {
            "type": MonitorType.DOCKER,
            "name": "monitor 1",
            "docker_container": "test",
            "docker_host": docker_host_id
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_push(self):
        expected_monitor = {
            "type": MonitorType.PUSH,
            "name": "monitor 1"
        }
        monitor = self.do_test_monitor_type(expected_monitor)

        # https://github.com/lucasheld/ansible-uptime-kuma/issues/5
        self.assertIsNotNone(monitor["pushToken"])

    def test_monitor_type_steam(self):
        expected_monitor = {
            "type": MonitorType.STEAM,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "port": 8888
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_gamedig(self):
        game_list = self.api.get_game_list()
        game = game_list[0]["keys"][0]
        expected_monitor = {
            "type": MonitorType.GAMEDIG,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "port": 8888,
            "game": game
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_mqtt(self):
        expected_monitor = {
            "type": MonitorType.MQTT,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "port": 8888,
            "mqttUsername": "mqtt username",
            "mqttPassword": "mqtt password",
            "mqttTopic": "mqtt topic",
            "mqttSuccessMessage": "mqtt success message"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_sqlserver(self):
        expected_monitor = {
            "type": MonitorType.SQLSERVER,
            "name": "monitor 1",
            "databaseConnectionString": (
                "Server=127.0.0.1,8888;Database=test;User Id=1;"
                "Password=secret123;Encrypt=true;"
                "TrustServerCertificate=Yes;Connection Timeout=5"),
            "databaseQuery": "select getdate()",
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_postgres(self):
        expected_monitor = {
            "type": MonitorType.POSTGRES,
            "name": "monitor 1",
            "databaseConnectionString": "postgres://username:password@host:port/database",
            "databaseQuery": "select getdate()"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_mysql(self):
        expected_monitor = {
            "type": MonitorType.MYSQL,
            "name": "monitor 1",
            "databaseConnectionString": "mysql://username:password@host:port/database",
            "databaseQuery": "select getdate()"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_mongodb(self):
        expected_monitor = {
            "type": MonitorType.MONGODB,
            "name": "monitor 1",
            "databaseConnectionString": "mongodb://username:password@host:port/database"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_radius(self):
        expected_monitor = {
            "type": MonitorType.RADIUS,
            "name": "monitor 1",
            "radiusUsername": "123",
            "radiusPassword": "456",
            "radiusSecret": "789",
            "radiusCalledStationId": "1",
            "radiusCallingStationId": "2"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_redis(self):
        expected_monitor = {
            "type": MonitorType.REDIS,
            "name": "monitor 1",
            "databaseConnectionString": "redis://user:password@host:port"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_group(self):
        # create monitor group
        expected_monitor = {
            "type": MonitorType.GROUP,
            "name": "monitor 1"
        }
        group_monitor = self.do_test_monitor_type(expected_monitor)
        group_monitor_id = group_monitor["id"]

        # use monitor group as parent for another monitor
        expected_monitor = {
            "type": MonitorType.PUSH,
            "name": "monitor 1",
            "parent": group_monitor_id
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_json_query(self):
        expected_monitor = {
            "type": MonitorType.JSON_QUERY,
            "name": "monitor 1",
            "url": "http://127.0.0.1",
            "jsonPath": "address.country",
            "expectedValue": "germany",
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_real_browser(self):
        expected_monitor = {
            "type": MonitorType.REAL_BROWSER,
            "name": "monitor 1",
            "url": "http://127.0.0.1",
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_kafka_producer(self):
        expected_monitor = {
            "type": MonitorType.KAFKA_PRODUCER,
            "name": "monitor 1",
            "kafkaProducerTopic": "topic",
            "kafkaProducerMessage": "message",
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_tailscale_ping(self):
        expected_monitor = {
            "type": MonitorType.TAILSCALE_PING,
            "name": "monitor 1",
            "hostname": "127.0.0.1"
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_ntp(self):
        expected_monitor = {
            "type": MonitorType.NTP,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "ntpStratumThreshold": 3,
            "ntpTimeOffsetThreshold": 50,
            "ntpRootDispersionThreshold": 20,
        }
        self.do_test_monitor_type(expected_monitor)

    def test_monitor_type_system_service(self):
        monitor = self.do_test_monitor_type({
            "type": MonitorType.SYSTEM_SERVICE,
            "name": "monitor 1",
            "system_service_name": "nginx",
        })
        self.assertEqual(monitor["system_service_name"], "nginx")

    def test_monitor_type_pm2(self):
        self.do_test_monitor_type({
            "type": MonitorType.PM2,
            "name": "monitor 1",
            "system_service_name": "api",
        })

    def test_system_service_name_is_changed_by_edit(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.SYSTEM_SERVICE, name="monitor 1",
            system_service_name="nginx")["monitorID"]
        self.api.edit_monitor(monitor_id, system_service_name="sshd")
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(monitor["system_service_name"], "sshd")
        self.assertEqual(monitor["name"], "monitor 1")

    def test_system_service_name_rejected_by_the_server(self):
        # the client only rejects blank names; the server checks the characters
        with self.assertRaises(UptimeKumaException):
            self.api.add_monitor(type=MonitorType.SYSTEM_SERVICE,
                                 name="monitor 1",
                                 system_service_name="not a service")
        self.assertEqual(self.api.get_monitors(), [])

    def test_monitor_type_sip_options(self):
        monitor = self.do_test_monitor_type({
            "type": MonitorType.SIP_OPTIONS,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "port": 5060,
        })
        self.assertEqual((monitor["hostname"], monitor["port"]),
                         ("127.0.0.1", 5060))

    def test_monitor_type_smtp(self):
        for security in ("secure", "starttls", "nostarttls"):
            with self.subTest(security=security):
                self.do_test_monitor_type({
                    "type": MonitorType.SMTP,
                    "name": "monitor 1",
                    "hostname": "127.0.0.1",
                    "port": 465,
                    "smtpSecurity": security,
                })

    def test_smtp_security_is_changed_by_edit_and_keeps_the_host(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.SMTP, name="monitor 1", hostname="127.0.0.1",
            port=465, smtpSecurity="secure")["monitorID"]
        self.api.edit_monitor(monitor_id, smtpSecurity="starttls", port=587)
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(
            (monitor["smtpSecurity"], monitor["port"], monitor["hostname"]),
            ("starttls", 587, "127.0.0.1"))

    def test_monitor_type_oracledb(self):
        monitor = self.do_test_monitor_type({
            "type": MonitorType.ORACLEDB,
            "name": "monitor 1",
            "databaseConnectionString": "127.0.0.1:1521/XEPDB1",
            "basic_auth_user": "scott",
            "basic_auth_pass": "tiger",
            "databaseQuery": "SELECT 1 FROM DUAL",
        })
        self.assertEqual(monitor["basic_auth_user"], "scott")

    def test_monitor_type_websocket_upgrade(self):
        monitor = self.do_test_monitor_type({
            "type": MonitorType.WEBSOCKET_UPGRADE,
            "name": "monitor 1",
            "url": "ws://127.0.0.1:9/socket",
            "wsSubprotocol": "soap,mqtt",
            "wsIgnoreSecWebsocketAcceptHeader": True,
        })
        self.assertEqual(monitor["wsSubprotocol"], "soap,mqtt")

    def test_websocket_upgrade_defaults_to_close_code_1000_and_goes_up(self):
        # Kuma's own socket.io endpoint accepts a websocket upgrade
        monitor_id = self.api.add_monitor(
            type=MonitorType.WEBSOCKET_UPGRADE, name="monitor 1",
            url="ws://127.0.0.1:3001/socket.io/?EIO=4&transport=websocket",
            interval=20, retryInterval=20)["monitorID"]
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(monitor["accepted_statuscodes"], ["1000"])
        self.wait_for_status(monitor_id, MonitorStatus.UP)
        self.api.edit_monitor(monitor_id, accepted_statuscodes=["1001"])
        self.assertEqual(
            self.api.get_monitor(monitor_id)["accepted_statuscodes"], ["1001"])

    def test_websocket_upgrade_flag_is_changed_by_edit(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.WEBSOCKET_UPGRADE, name="monitor 1",
            url="ws://127.0.0.1:9/socket")["monitorID"]
        monitor = self.api.get_monitor(monitor_id)
        self.assertFalse(monitor["wsIgnoreSecWebsocketAcceptHeader"])
        self.api.edit_monitor(
            monitor_id, wsIgnoreSecWebsocketAcceptHeader=True
        )
        monitor = self.api.get_monitor(monitor_id)
        self.assertTrue(monitor["wsIgnoreSecWebsocketAcceptHeader"])
        self.assertEqual(monitor["url"], "ws://127.0.0.1:9/socket")

    def test_monitor_type_snmp(self):
        monitor = self.do_test_monitor_type({
            "type": MonitorType.SNMP,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "snmpOid": "1.3.6.1.2.1.1.3.0",
            "snmpVersion": "1",
            "radiusPassword": "public",
            "jsonPath": "$",
            "jsonPathOperator": ">=",
            "expectedValue": "0",
        })
        self.assertEqual(monitor["port"], 161)

    def test_snmp_timeout_defaults_to_5(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.SNMP, name="monitor 1", hostname="127.0.0.1",
            snmpOid="1.3.6.1.2.1.1.3.0", radiusPassword="public",
            expectedValue="0")["monitorID"]
        self.assertEqual(self.api.get_monitor(monitor_id)["timeout"], 5)

    def test_snmp_is_changed_by_edit_and_keeps_the_rest(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.SNMP, name="monitor 1", hostname="127.0.0.1",
            snmpOid="1.3.6.1.2.1.1.3.0", radiusPassword="public",
            expectedValue="0")["monitorID"]
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual((monitor["snmpVersion"], monitor["jsonPathOperator"],
                          monitor["jsonPath"]), ("2c", "==", "$"))
        self.api.edit_monitor(monitor_id, jsonPathOperator="contains",
                              snmpOid="1.3.6.1.2.1.1.5.0")
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(
            (monitor["jsonPathOperator"], monitor["snmpOid"],
             monitor["hostname"], monitor["snmpVersion"]),
            ("contains", "1.3.6.1.2.1.1.5.0", "127.0.0.1", "2c"))

    def test_monitor_type_sftp(self):
        monitor = self.do_test_monitor_type({
            "type": MonitorType.SFTP,
            "name": "monitor 1",
            "hostname": "127.0.0.1",
            "sshUsername": "user",
            "sshPassword": "secret",
            "sftpPath": "/tmp",
        })
        self.assertEqual(monitor["port"], 22)
        self.assertEqual(monitor["sshAuthMethod"], "password")

    def test_sftp_private_key_and_switching_the_method(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.SFTP, name="monitor 1", hostname="127.0.0.1",
            sshUsername="user", sshAuthMethod="privateKey",
            sshPrivateKey="not-a-real-key", sshPassphrase="phrase",
            port=2222)["monitorID"]
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(
            (monitor["sshAuthMethod"], monitor["sshPrivateKey"],
             monitor["port"]), ("privateKey", "not-a-real-key", 2222))
        self.api.edit_monitor(monitor_id, sshAuthMethod="password",
                              sshPassword="secret")
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual((monitor["sshAuthMethod"], monitor["sshPassword"],
                          monitor["hostname"]),
                         ("password", "secret", "127.0.0.1"))
        # edit sends the stored value of the other method back unchanged
        self.assertEqual(monitor["sshPrivateKey"], "not-a-real-key")

    def test_monitor_type_rabbitmq(self):
        self.do_test_monitor_type({
            "type": MonitorType.RABBITMQ,
            "name": "monitor 1",
            "rabbitmqNodes": ["http://127.0.0.1:15672", "https://example.org"],
            "rabbitmqUsername": "guest",
            "rabbitmqPassword": "guest",
        })

    def test_rabbitmq_is_changed_by_edit_and_keeps_the_rest(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.RABBITMQ, name="monitor 1",
            rabbitmqNodes=["http://127.0.0.1:15672"],
            rabbitmqUsername="guest", rabbitmqPassword="guest")["monitorID"]
        self.api.edit_monitor(monitor_id, rabbitmqUsername="admin")
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(
            (monitor["rabbitmqNodes"], monitor["rabbitmqUsername"],
             monitor["rabbitmqPassword"]),
            (["http://127.0.0.1:15672"], "admin", "guest"))

    def test_monitor_type_globalping_ping(self):
        monitor = self.do_test_monitor_type({
            "type": MonitorType.GLOBALPING,
            "name": "monitor 1",
            "subtype": "ping",
            "hostname": "example.org",
            "location": "germany",
            "protocol": "TCP",
            "port": 443,
            "ipFamily": "ipv4",
            "ping_count": 5,
        })
        self.assertEqual(monitor["ping_count"], 5)

    def test_monitor_type_globalping_http(self):
        self.do_test_monitor_type({
            "type": MonitorType.GLOBALPING,
            "name": "monitor 1",
            "subtype": "http",
            "url": "https://example.org/path?q=1",
            "location": "world",
            "protocol": "HTTP2",
            "method": "HEAD",
            "cacheBust": True,
            "accepted_statuscodes": ["200-299", "301"],
            "authMethod": AuthMethod.BEARER,
            "bearer_token": "token",
        })

    def test_monitor_type_globalping_dns(self):
        monitor = self.do_test_monitor_type({
            "type": MonitorType.GLOBALPING,
            "name": "monitor 1",
            "subtype": "dns",
            "hostname": "example.org",
            "dns_resolve_type": "DNSKEY",
            "dns_resolve_server": "8.8.8.8",
            "protocol": "TCP",
        })
        self.assertEqual(monitor["port"], 53)

    def test_globalping_defaults_and_edit_keep_the_rest(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.GLOBALPING, name="monitor 1",
            hostname="example.org")["monitorID"]
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(
            (monitor["subtype"], monitor["location"], monitor["protocol"],
             monitor["ping_count"], monitor["port"]),
            ("ping", "world", "ICMP", 3, 80))
        self.api.edit_monitor(monitor_id, location="amazon+germany")
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(
            (monitor["location"], monitor["hostname"], monitor["protocol"]),
            ("amazon+germany", "example.org", "ICMP"))

    def test_globalping_subtype_change_resets_port_and_protocol(self):
        monitor_id = self.api.add_monitor(
            type=MonitorType.GLOBALPING, name="monitor 1",
            hostname="example.org")["monitorID"]
        self.api.edit_monitor(monitor_id, subtype="dns")
        monitor = self.api.get_monitor(monitor_id)
        self.assertEqual(
            (monitor["subtype"], monitor["protocol"], monitor["port"],
             monitor["hostname"]), ("dns", "UDP", 53, "example.org"))

    def wait_for_status(self, monitor_id, status, timeout=30):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                if self.api.get_monitor_status(monitor_id) == status:
                    return
            except UptimeKumaException:
                pass  # no heartbeat yet
            time.sleep(0.5)
        self.assertEqual(self.api.get_monitor_status(monitor_id), status)

    def test_monitor_type_manual(self):
        # the server does not return manual_status, so check the heartbeat
        monitor_id = self.api.add_monitor(
            type=MonitorType.MANUAL, name="monitor 1", manual_status=1,
            interval=20, retryInterval=20)["monitorID"]
        self.wait_for_status(monitor_id, MonitorStatus.UP)
        self.api.edit_monitor(monitor_id, name="monitor 2")
        self.assertEqual(self.api.get_monitor(monitor_id)["name"], "monitor 2")
        self.wait_for_status(monitor_id, MonitorStatus.UP)
        self.api.edit_monitor(monitor_id, manual_status=0)
        self.wait_for_status(monitor_id, MonitorStatus.DOWN)
        self.api.edit_monitor(monitor_id, manual_status=1)
        self.wait_for_status(monitor_id, MonitorStatus.UP)

    def test_delete_not_existing_monitor(self):
        with self.assertRaises(UptimeKumaException):
            self.api.delete_monitor(42)


if __name__ == '__main__':
    unittest.main()
