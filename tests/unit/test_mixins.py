"""Behaviour of the per-domain mixins against the fake Socket.IO client."""
import pytest

from tests.unit.fake_kuma import make_api
from uptime_kuma_api import (
    DockerType,
    Event,
    MaintenanceStrategy,
    ProxyProtocol,
    Timeout,
    UptimeKumaException,
)


class Base:
    @pytest.fixture(autouse=True)
    def _setup(self):
        self.api = make_api()
        self.sio = self.api.sio
        self.data = self.api._event_data


class TestPassThroughCalls(Base):
    """Methods that send one event and return the reply."""

    CASES = [
        ("twofa_status", (), "twoFAStatus"),
        ("prepare_2fa", ("pw",), "prepare2FA"),
        ("save_2fa", ("pw",), "save2FA"),
        ("disable_2fa", ("pw",), "disable2FA"),
        ("login_by_token", ("tok",), "loginByToken"),
        ("logout", (), "logout"),
        ("need_setup", (), "needSetup"),
        ("clear_events", (3,), "clearEvents"),
        ("clear_heartbeats", (3,), "clearHeartbeats"),
        ("clear_statistics", (), "clearStatistics"),
        ("get_database_size", (), "getDatabaseSize"),
        ("shrink_database", (), "shrinkDatabase"),
        ("pause_monitor", (3,), "pauseMonitor"),
        ("resume_monitor", (3,), "resumeMonitor"),
        ("pause_maintenance", (3,), "pauseMaintenance"),
        ("resume_maintenance", (3,), "resumeMaintenance"),
        ("test_chrome", ("/usr/bin/chrome",), "testChrome"),
        ("check_apprise", (), "checkApprise"),
    ]

    @pytest.mark.parametrize("name, args, event", CASES)
    def test_each_method_sends_its_event(self, name, args, event):
        self.sio.replies[event] = {"ok": True, "x": 1}
        result = getattr(self.api, name)(*args)
        expected = args[0] if len(args) == 1 else None
        assert self.sio.calls == [(event, expected)]
        assert result == {"x": 1}

    def test_arguments_are_forwarded(self):
        self.api.setup("admin", "pw")
        self.api.verify_token("123456", "pw")
        self.api.change_password("old", "new")
        assert self.sio.sent("setup") == [("admin", "pw")]
        assert self.sio.sent("verifyToken") == [("123456", "pw")]
        assert self.sio.sent("changePassword") == [
            {"currentPassword": "old", "newPassword": "new"}
        ]

    def test_wrapped_replies(self):
        self.sio.replies["getMonitorBeats"] = {
            "ok": True,
            "data": [{"important": 1}],
        }
        self.sio.replies["getGameList"] = {"ok": True, "gameList": ["g"]}
        self.sio.replies["getMonitorMaintenance"] = {"ok": True,
                                                     "monitors": [{"id": 1}]}
        self.sio.replies["getMaintenanceStatusPage"] = {
            "ok": True, "statusPages": [{"id": 2}]}
        assert self.api.get_monitor_beats(1, 24) == [{"important": True}]
        assert self.sio.sent("getMonitorBeats") == [(1, 24)]
        assert self.api.get_game_list() == ["g"]
        assert self.api.get_monitor_maintenance(1) == [{"id": 1}]
        assert self.api.get_status_page_maintenance(1) == [{"id": 2}]

    def test_maintenance_links(self):
        self.api.add_monitor_maintenance(5, [{"id": 1}])
        self.api.add_status_page_maintenance(5, [{"id": 2}])
        assert self.sio.sent("addMonitorMaintenance") == [(5, [{"id": 1}])]
        assert self.sio.sent("addMaintenanceStatusPage") == [(5, [{"id": 2}])]

    def test_server_error_is_raised(self):
        self.sio.replies["twoFAStatus"] = {"ok": False, "msg": "bad"}
        with pytest.raises(UptimeKumaException, match="bad"):
            self.api.twofa_status()


class TestLogin(Base):
    def test_login_sends_credentials(self):
        self.sio.replies["login"] = {"ok": True, "token": "t"}
        assert self.api.login("u", "p", token="123") == {"token": "t"}
        assert self.sio.sent("login") == [
            {"username": "u", "password": "p", "token": "123"}
        ]

    @pytest.mark.parametrize("username, password", [
        ("u", None),
        (None, "p"),
        ("", None),
        (None, ""),
    ])
    def test_login_with_only_one_credential_is_rejected(
            self, username, password):
        with pytest.raises(ValueError, match="together"):
            self.api.login(username, password)
        # nothing reached the server
        assert self.sio.calls == []

    def test_empty_string_credentials_are_still_sent(self):
        self.sio.replies["login"] = {"ok": False, "msg": "bad"}
        with pytest.raises(UptimeKumaException):
            self.api.login("", "")
        assert self.sio.sent("login")[0]["username"] == ""

    def test_auto_login_succeeds_when_the_event_arrives(self):
        self.api._event_auto_login()
        assert self.api.login() == {}
        assert self.sio.calls == []

    def test_auto_login_without_the_event_times_out_with_a_hint(self):
        with pytest.raises(Timeout) as ctx:
            self.api.login()
        assert "disableAuth" in str(ctx.value)


class TestApiKeys(Base):
    @pytest.fixture(autouse=True)
    def _setup_more(self, _setup):
        self.data[Event.API_KEY_LIST] = [{"id": 1, "name": "k"}]

    def test_get(self):
        assert self.api.get_api_keys() == [{"id": 1, "name": "k"}]
        assert self.api.get_api_key(1)["name"] == "k"
        with pytest.raises(
            UptimeKumaException, match="api key does not exist"
        ):
            self.api.get_api_key(2)

    def test_add_converts_active_to_int(self):
        self.api.add_api_key("n", "2030-01-01", True)
        self.api.add_api_key("n", None, False)
        sent = self.sio.sent("addAPIKey")
        assert [s["active"] for s in sent] == [1, 0]
        assert sent[0]["name"] == "n"

    def test_enable_disable_delete(self):
        self.api.enable_api_key(1)
        self.api.disable_api_key(1)
        self.api.delete_api_key(1)
        assert self.sio.sent("enableAPIKey") == [1]
        assert self.sio.sent("disableAPIKey") == [1]
        assert self.sio.sent("deleteAPIKey") == [1]

    def test_delete_unknown_does_not_call_the_server(self):
        with pytest.raises(UptimeKumaException):
            self.api.delete_api_key(9)
        assert self.sio.calls == []


class TestDockerHosts(Base):
    @pytest.fixture(autouse=True)
    def _setup_more(self, _setup):
        self.data[Event.DOCKER_HOST_LIST] = [
            {"id": 1, "name": "h", "dockerType": "socket",
             "dockerDaemon": "/var/run/docker.sock"}]

    def test_get(self):
        hosts = self.api.get_docker_hosts()
        assert hosts[0]["dockerType"] == DockerType.SOCKET
        assert self.api.get_docker_host(1)["name"] == "h"
        with pytest.raises(UptimeKumaException):
            self.api.get_docker_host(2)

    def test_add_and_test_default_the_daemon(self):
        self.api.add_docker_host(name="a", dockerType=DockerType.SOCKET)
        self.api.add_docker_host(name="b", dockerType=DockerType.TCP)
        self.api.test_docker_host(name="c", dockerType=DockerType.TCP,
                                  dockerDaemon="tcp://x:1")
        sent = self.sio.sent("addDockerHost")
        assert sent[0][0]["dockerDaemon"] == "/var/run/docker.sock"
        assert sent[1][0]["dockerDaemon"] == "tcp://localhost:2375"
        assert sent[0][1] is None
        assert self.sio.sent("testDockerHost")[0]["dockerDaemon"] == "tcp://x:1"

    def test_edit_merges_into_the_current_host(self):
        self.api.edit_docker_host(1, name="renamed")
        data, id_ = self.sio.sent("addDockerHost")[0]
        assert (data["name"], id_) == ("renamed", 1)

    def test_delete(self):
        self.api.delete_docker_host(1)
        assert self.sio.sent("deleteDockerHost") == [1]
        with pytest.raises(UptimeKumaException):
            self.api.delete_docker_host(2)


class TestProxies(Base):
    @pytest.fixture(autouse=True)
    def _setup_more(self, _setup):
        self.data[Event.PROXY_LIST] = [
            {"id": 1, "protocol": "http", "host": "h", "port": 80,
             "auth": 0, "active": 1, "default": 0}]

    def test_get(self):
        proxy = self.api.get_proxy(1)
        assert proxy["protocol"] == ProxyProtocol.HTTP
        assert proxy["auth"] is False
        assert len(self.api.get_proxies()) == 1
        with pytest.raises(UptimeKumaException):
            self.api.get_proxy(2)

    def test_add(self):
        self.api.add_proxy(protocol=ProxyProtocol.HTTP, host="h", port=80)
        data, id_ = self.sio.sent("addProxy")[0]
        assert (data["host"], id_) == ("h", None)

    def test_add_with_auth_needs_credentials(self):
        with pytest.raises(TypeError):
            self.api.add_proxy(protocol=ProxyProtocol.HTTP, host="h",
                               port=80, auth=True)

    def test_add_requires_the_basic_arguments(self):
        with pytest.raises(TypeError):
            self.api.add_proxy(protocol=ProxyProtocol.HTTP)

    def test_edit_and_delete(self):
        self.api.edit_proxy(1, host="new")
        data, id_ = self.sio.sent("addProxy")[0]
        assert (data["host"], id_) == ("new", 1)
        self.api.delete_proxy(1)
        assert self.sio.sent("deleteProxy") == [1]
        with pytest.raises(UptimeKumaException):
            self.api.delete_proxy(2)


class TestTags(Base):
    def test_tag_crud(self):
        self.sio.replies["getTags"] = {
            "ok": True,
            "tags": [{"id": 1, "name": "n", "color": "c"}],
        }
        self.sio.replies["addTag"] = {"ok": True, "tag": {"id": 2}}
        assert self.api.get_tags()[0]["id"] == 1
        assert self.api.get_tag(1)["name"] == "n"
        with pytest.raises(UptimeKumaException):
            self.api.get_tag(9)
        assert self.api.add_tag(name="n", color="#fff") == {"id": 2}
        assert self.sio.sent("addTag")[0]["new"]
        self.api.edit_tag(1, color="#000")
        assert self.sio.sent("editTag")[0]["color"] == "#000"
        self.api.delete_tag(1)
        assert self.sio.sent("deleteTag") == [1]
        with pytest.raises(UptimeKumaException):
            self.api.delete_tag(9)

    def test_add_tag_requires_arguments(self):
        with pytest.raises(TypeError):
            self.api.add_tag(name="n")

    def test_add_monitor_tag_refreshes_the_cached_monitor(self):
        self.data[Event.MONITOR_LIST] = {"7": {"id": 7, "tags": []}}
        self.sio.replies["getMonitor"] = {
            "ok": True, "monitor": {"id": 7, "tags": [{"tag_id": 1}]}}
        self.api.add_monitor_tag(1, 7, "v")
        assert self.sio.sent("addMonitorTag") == [(1, 7, "v")]
        assert self.data[Event.MONITOR_LIST]["7"]["tags"] == [{"tag_id": 1}]

    def test_add_monitor_tag_without_a_cache_skips_the_refresh(self):
        self.api.add_monitor_tag(1, 7)
        assert self.sio.sent("getMonitor") == []

    def test_delete_monitor_tag(self):
        monitor = {"id": 7, "type": "http", "notificationIDList": {}, "tags": [
            {"monitor_id": 7, "tag_id": 1, "value": ""}]}
        self.data[Event.MONITOR_LIST] = {"7": monitor}
        self.sio.replies["getMonitor"] = {"ok": True, "monitor": monitor}
        self.api.delete_monitor_tag(1, 7)
        assert self.sio.sent("deleteMonitorTag") == [(1, 7, "")]

    def test_delete_unknown_monitor_tag(self):
        self.data[Event.MONITOR_LIST] = {"7": {"id": 7, "type": "http",
                                               "notificationIDList": {},
                                               "tags": []}}
        with pytest.raises(UptimeKumaException):
            self.api.delete_monitor_tag(1, 7)


class TestHeartbeatsAndInfo(Base):
    def test_cache_getters(self):
        self.data[Event.AVG_PING] = {1: 5}
        self.data[Event.UPTIME] = {1: {24: 1}}
        self.data[Event.CERT_INFO] = {1: {}}
        assert self.api.avg_ping() == {1: 5}
        assert self.api.uptime() == {1: {24: 1}}
        assert self.api.cert_info() == {1: {}}
        assert self.api.info() == {"version": "2.5.6"}

    def test_heartbeats_are_converted(self):
        beat = {"monitorID": 1, "status": 1, "important": 1}
        self.data[Event.HEARTBEAT_LIST] = {1: [dict(beat)]}
        self.data[Event.IMPORTANT_HEARTBEAT_LIST] = {1: [dict(beat)]}
        for r in (self.api.get_heartbeats(),
                  self.api.get_important_heartbeats()):
            assert r[1][0]["important"] is True
            assert int(r[1][0]["status"]) == 1

    def test_monitor_status(self):
        self.data[Event.HEARTBEAT_LIST] = {
            1: [{"status": 0, "important": 0}, {"status": 1, "important": 0}]}
        assert int(self.api.get_monitor_status(1)) == 1
        with pytest.raises(UptimeKumaException):
            self.api.get_monitor_status(2)


class TestSettings(Base):
    def test_get_settings(self):
        self.sio.replies["getSettings"] = {"ok": True, "data": {"a": 1}}
        assert self.api.get_settings() == {"a": 1}

    def test_set_settings_keeps_unspecified_values(self):
        self.sio.replies["getSettings"] = {
            "ok": True,
            "data": {"keepDataPeriodDays": 180, "tlsExpiryNotifyDays": [7]},
        }
        self.api.set_settings(keepDataPeriodDays=30, password="pw")
        data, password = self.sio.sent("setSettings")[0]
        assert data["keepDataPeriodDays"] == 30
        assert data["tlsExpiryNotifyDays"] == [7]
        assert password == "pw"

    def test_upload_backup_validates_the_import_handle(self):
        self.api.upload_backup("{}", "overwrite")
        assert self.sio.sent("uploadBackup") == [("{}", "overwrite")]
        with pytest.raises(ValueError):
            self.api.upload_backup("{}", "bogus")


class TestMaintenance(Base):
    def test_get(self):
        self.data[Event.MAINTENANCE_LIST] = {"1": {"id": 1}}
        assert self.api.get_maintenances() == [{"id": 1}]
        self.sio.replies["getMaintenance"] = {
            "ok": True, "maintenance": {"id": 1, "title": "t"}}
        assert self.api.get_maintenance(1)["title"] == "t"

    def test_add_applies_defaults(self):
        self.api.add_maintenance(title="t",
                                 strategy=MaintenanceStrategy.MANUAL)
        data = self.sio.sent("addMaintenance")[0]
        assert data["title"] == "t"
        assert data["timeRange"][0]["hours"] == 2

    def test_add_requires_the_strategy_arguments(self):
        with pytest.raises(TypeError):
            self.api.add_maintenance(title="t")

    def test_edit_and_delete(self):
        self.sio.replies["getMaintenance"] = {
            "ok": True, "maintenance": {"id": 1, "title": "t",
                            "strategy": "manual"}}
        self.api.edit_maintenance(1, title="new")
        assert self.sio.sent("editMaintenance")[0]["title"] == "new"
        self.data[Event.MAINTENANCE_LIST] = {"1": {"id": 1}}
        self.api.delete_maintenance(1)
        assert self.sio.sent("deleteMaintenance") == [1]
        with pytest.raises(UptimeKumaException):
            self.api.delete_maintenance(2)
