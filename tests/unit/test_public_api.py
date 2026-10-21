from uptime_kuma_api import UptimeKumaApi

# Snapshot of the public names of UptimeKumaApi taken before it was split into
# per-domain mixins (#35). Adding or removing a public method must be a
# deliberate change to this list.
PUBLIC_METHODS = [
    "add_api_key",
    "add_docker_host",
    "add_maintenance",
    "add_monitor",
    "add_monitor_maintenance",
    "add_monitor_tag",
    "add_notification",
    "add_proxy",
    "add_status_page",
    "add_status_page_maintenance",
    "add_tag",
    "avg_ping",
    "cert_info",
    "change_password",
    "check_apprise",
    "clear_events",
    "clear_heartbeats",
    "clear_statistics",
    "connect",
    "delete_api_key",
    "delete_docker_host",
    "delete_incident",
    "delete_maintenance",
    "delete_monitor",
    "delete_monitor_tag",
    "delete_notification",
    "delete_proxy",
    "delete_status_page",
    "delete_tag",
    "disable_2fa",
    "disable_api_key",
    "disconnect",
    "edit_docker_host",
    "edit_incident",
    "edit_maintenance",
    "edit_monitor",
    "edit_notification",
    "edit_proxy",
    "edit_tag",
    "enable_api_key",
    "get_api_key",
    "get_api_keys",
    "get_database_size",
    "get_docker_host",
    "get_docker_hosts",
    "get_game_list",
    "get_heartbeats",
    "get_important_heartbeats",
    "get_incident_history",
    "get_maintenance",
    "get_maintenances",
    "get_monitor",
    "get_monitor_beats",
    "get_monitor_maintenance",
    "get_monitor_status",
    "get_monitors",
    "get_notification",
    "get_notifications",
    "get_proxies",
    "get_proxy",
    "get_settings",
    "get_status_page",
    "get_status_page_maintenance",
    "get_status_pages",
    "get_tag",
    "get_tags",
    "info",
    "login",
    "login_by_token",
    "logout",
    "need_setup",
    "pause_maintenance",
    "pause_monitor",
    "post_incident",
    "prepare_2fa",
    "resolve_incident",
    "resume_maintenance",
    "resume_monitor",
    "save_2fa",
    "save_status_page",
    "set_settings",
    "setup",
    "shrink_database",
    "test_chrome",
    "test_docker_host",
    "test_notification",
    "twofa_status",
    "unpin_incident",
    "upload_backup",
    "uptime",
    "verify_token",
    "version",
    "wait_for_event",
]


class TestPublicApi:
    def test_public_names_are_unchanged(self):
        # mutmut adds trampoline attributes (x...__mutmut_N); they are not API
        names = sorted(
            n
            for n in dir(UptimeKumaApi)
            if not n.startswith(("_", "x\u01c1")) and "__mutmut" not in n
        )
        assert names == PUBLIC_METHODS

    def test_methods_are_defined_on_the_class_hierarchy(self):
        # every public name resolves to a callable or property on the class
        for name in PUBLIC_METHODS:
            assert hasattr(UptimeKumaApi, name)
