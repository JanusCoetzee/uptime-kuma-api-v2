from __future__ import annotations

import secrets
import string

from . import (
    AuthMethod,
    MonitorType
)
from ._helpers import (
    _check_argument_conditions,
    _check_missing_arguments,
    parse_value,
)


def _is_ws_close_code_or_range(value) -> bool:
    if not isinstance(value, str):
        return False
    parts = value.split("-")
    if len(parts) not in (1, 2) or not all(
            p.isascii() and p.isdigit() and 1000 <= int(p) <= 4999
            for p in parts):
        return False
    return len(parts) == 1 or int(parts[0]) <= int(parts[1])


GLOBALPING_PROTOCOLS = {
    "ping": ("ICMP", "TCP"),
    "http": ("HTTP2",),
    "dns": ("UDP", "TCP"),
}
GLOBALPING_DNS_TYPES = (
    "A", "AAAA", "ANY", "CNAME", "DNSKEY", "DS", "HTTPS", "MX", "NS",
    "NSEC", "PTR", "RRSIG", "SOA", "SRV", "SVCB", "TXT")


def _check_globalping(kwargs) -> None:
    subtype = kwargs.get("subtype")
    if subtype not in GLOBALPING_PROTOCOLS:
        raise ValueError(
            f"Unknown subtype value: {subtype!r}, "
            "expected 'ping', 'http' or 'dns'")
    _check_missing_arguments(
        ["url"] if subtype == "http" else ["hostname"], kwargs)

    location = kwargs.get("location")
    if not isinstance(location, str) or not location.strip():
        raise ValueError("location must be a non-empty string")
    if "," in location:
        # the form (and Globalping, which gets one magic location) allows one
        raise ValueError("location must be a single location, not a list")

    protocol = kwargs.get("protocol")
    if protocol is not None and protocol not in GLOBALPING_PROTOCOLS[subtype]:
        raise ValueError(
            f"Unknown protocol value: {protocol!r} for subtype {subtype!r}, "
            f"expected one of {', '.join(GLOBALPING_PROTOCOLS[subtype])}")

    ip_family = kwargs.get("ipFamily")
    if ip_family not in (None, "ipv4", "ipv6"):
        raise ValueError(
            f"Unknown ipFamily value: {ip_family!r}, "
            "expected 'ipv4' or 'ipv6'")

    if subtype == "dns" and (
            kwargs["dns_resolve_type"] not in GLOBALPING_DNS_TYPES):
        raise ValueError(
            f"Unknown dns_resolve_type value: {kwargs['dns_resolve_type']}")

    if subtype == "http" and kwargs.get("method") not in (
            "HEAD", "GET", "OPTIONS"):
        raise ValueError(
            f"Unknown method value: {kwargs.get('method')!r}, "
            "expected 'HEAD', 'GET' or 'OPTIONS'")


def parse_monitor_type(data) -> None:
    parse_value(data, "type", MonitorType)


def parse_auth_method(data) -> None:
    parse_value(data, "authMethod", AuthMethod, AuthMethod.NONE)


def gen_secret(length: int) -> str:
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def _convert_monitor_return(monitor) -> None:
    if isinstance(monitor["notificationIDList"], dict):
        monitor["notificationIDList"] = [
            int(i) for i in monitor["notificationIDList"].keys()]


def _convert_monitor_input(kwargs) -> None:
    if not kwargs["accepted_statuscodes"]:
        kwargs["accepted_statuscodes"] = ["200-299"]

    dict_notification_ids = {}
    if kwargs["notificationIDList"]:
        for notification_id in kwargs["notificationIDList"]:
            dict_notification_ids[notification_id] = True
    kwargs["notificationIDList"] = dict_notification_ids

    if kwargs["type"] == MonitorType.PUSH and not kwargs.get("pushToken"):
        kwargs["pushToken"] = gen_secret(32)


def _check_arguments_monitor(kwargs) -> None:
    required_args = [
        "type",
        "name",
        "interval",
        "maxretries",
        "retryInterval"
    ]
    _check_missing_arguments(required_args, kwargs)

    required_args_by_type = {
        MonitorType.HTTP: ["url", "maxredirects"],
        MonitorType.PORT: ["hostname", "port"],
        MonitorType.PING: ["hostname"],
        MonitorType.KEYWORD: ["url", "keyword", "maxredirects"],
        MonitorType.GRPC_KEYWORD: [
            "grpcUrl", "keyword", "grpcServiceName", "grpcMethod"],
        MonitorType.DNS: ["hostname", "dns_resolve_server", "port"],
        MonitorType.DOCKER: ["docker_container", "docker_host"],
        MonitorType.PUSH: [],
        MonitorType.STEAM: ["hostname", "port"],
        MonitorType.GAMEDIG: ["game", "hostname", "port"],
        MonitorType.MQTT: ["hostname", "port", "mqttTopic"],
        MonitorType.SQLSERVER: ["databaseConnectionString"],
        MonitorType.POSTGRES: ["databaseConnectionString"],
        MonitorType.MYSQL: ["databaseConnectionString"],
        MonitorType.MONGODB: ["databaseConnectionString"],
        MonitorType.RADIUS: [
            "radiusUsername", "radiusPassword", "radiusSecret",
            "radiusCalledStationId", "radiusCallingStationId"],
        MonitorType.REDIS: ["databaseConnectionString"],
        MonitorType.GROUP: [],
        MonitorType.JSON_QUERY: ["url", "jsonPath", "expectedValue"],
        MonitorType.REAL_BROWSER: ["url"],
        MonitorType.KAFKA_PRODUCER: [
            "kafkaProducerTopic", "kafkaProducerMessage"],
        MonitorType.TAILSCALE_PING: ["hostname"],
        MonitorType.NTP: ["hostname"],
        MonitorType.SYSTEM_SERVICE: ["system_service_name"],
        MonitorType.PM2: ["system_service_name"],
        MonitorType.MANUAL: [],
        MonitorType.SIP_OPTIONS: ["hostname", "port"],
        MonitorType.SMTP: ["hostname", "port"],
        MonitorType.ORACLEDB: ["databaseConnectionString"],
        MonitorType.WEBSOCKET_UPGRADE: ["url"],
        MonitorType.SNMP: [
            "hostname", "snmpOid", "radiusPassword", "expectedValue"],
        MonitorType.SFTP: ["hostname", "sshUsername"],
        MonitorType.RABBITMQ: [
            "rabbitmqNodes", "rabbitmqUsername", "rabbitmqPassword"],
        # the rest depends on the subtype, checked below
        MonitorType.GLOBALPING: [],
    }
    type_ = kwargs["type"]
    if type_ not in required_args_by_type:
        raise ValueError(f"unsupported monitor type: {type_}")
    required_args = required_args_by_type[type_]
    _check_missing_arguments(required_args, kwargs)
    if kwargs.get("authMethod") == AuthMethod.BEARER:
        _check_missing_arguments(["bearer_token"], kwargs)
    if type_ == MonitorType.GLOBALPING:
        _check_globalping(kwargs)

    conditions = dict(
        interval=dict(
            min=20,
        ),
        maxretries=dict(
            min=0,
        ),
        retryInterval=dict(
            min=20,
        ),
        maxredirects=dict(
            min=0,
        ),
        port=dict(
            min=0,
            max=65535,
        ),
        ping_count=dict(
            min=1,
            max=100,
        ),
        ntpStratumThreshold=dict(
            min=1,
            max=15,
        ),
        ntpTimeOffsetThreshold=dict(
            min=1,
        ),
        ntpRootDispersionThreshold=dict(
            min=1,
        ),
    )
    _check_argument_conditions(conditions, kwargs)

    allowed_accepted_statuscodes = [
        "100-199",
        "200-299",
        "300-399",
        "400-499",
        "500-599",
    ] + [
        str(i) for i in range(100, 999 + 1)
    ]
    accepted_statuscodes = kwargs["accepted_statuscodes"]
    for accepted_statuscode in accepted_statuscodes:
        if type_ == MonitorType.WEBSOCKET_UPGRADE:
            # compared with the websocket close code, not an HTTP status
            if not _is_ws_close_code_or_range(accepted_statuscode):
                raise ValueError(
                    f"Unknown accepted_statuscodes value: "
                    f"{accepted_statuscode!r}, expected a websocket close "
                    "code 'NNNN' (1000-4999) or a range such as "
                    "'1000-1003'")
        elif accepted_statuscode not in allowed_accepted_statuscodes:
            raise ValueError(
                f"Unknown accepted_statuscodes value: "
                f"{accepted_statuscode!r}, expected 'NNN' (100-999) or "
                "'N00-N99' (for example '200-299')")

    dns_resolve_type = kwargs["dns_resolve_type"]
    # globalping has more record types, checked in _check_globalping
    if type_ != MonitorType.GLOBALPING and dns_resolve_type not in [
        "A",
        "AAAA",
        "CAA",
        "CNAME",
        "MX",
        "NS",
        "PTR",
        "SOA",
        "SRV",
        "TXT",
    ]:
        raise ValueError(f"Unknown dns_resolve_type value: {dns_resolve_type}")

    if type_ in (MonitorType.SYSTEM_SERVICE, MonitorType.PM2):
        # the server trims the name and rejects an empty one
        if not str(kwargs["system_service_name"]).strip():
            raise ValueError("system_service_name must not be empty")

    if type_ == MonitorType.SMTP:
        smtp_security = kwargs.get("smtpSecurity")
        if smtp_security not in (None, "secure", "starttls", "nostarttls"):
            raise ValueError(
                f"Unknown smtpSecurity value: {smtp_security!r}, "
                "expected 'secure', 'starttls' or 'nostarttls'")

    if type_ == MonitorType.SNMP:
        # Kuma 2.5.6 never saves the SNMPv3 username, so v3 cannot work yet
        snmp_version = kwargs.get("snmpVersion")
        if snmp_version not in (None, "1", "2c"):  # None: the default
            raise ValueError(
                f"Unknown snmpVersion value: {snmp_version!r}, "
                "expected '1' or '2c' (SNMPv3 is not supported by Kuma 2.5.6)")
        operator = kwargs.get("jsonPathOperator")
        if operator not in (
                None, ">", ">=", "<", "<=", "!=", "==", "contains"):
            raise ValueError(
                f"Unknown jsonPathOperator value: {operator!r}, expected "
                "'>', '>=', '<', '<=', '!=', '==' or 'contains'")

    if type_ == MonitorType.SFTP:
        auth_method = kwargs.get("sshAuthMethod")
        if auth_method not in (None, "password", "privateKey"):
            raise ValueError(
                f"Unknown sshAuthMethod value: {auth_method!r}, "
                "expected 'password' or 'privateKey'")
        if auth_method == "privateKey":
            _check_missing_arguments(["sshPrivateKey"], kwargs)
        else:
            _check_missing_arguments(["sshPassword"], kwargs)

    if type_ == MonitorType.RABBITMQ:
        nodes = kwargs["rabbitmqNodes"]
        if (not isinstance(nodes, (list, tuple)) or not nodes or not all(
                isinstance(n, str) and n.startswith(("http://", "https://"))
                for n in nodes)):
            raise ValueError(
                "rabbitmqNodes must be a non-empty list of http:// or "
                "https:// URLs")

    if type_ == MonitorType.MANUAL:
        manual_status = kwargs.get("manual_status")
        if manual_status not in (None, 0, 1):
            raise ValueError(
                f"Unknown manual_status value: {manual_status!r}, "
                "expected 0 (down) or 1 (up)")

    if type_ == MonitorType.KAFKA_PRODUCER:
        # a missing or None option means the server default mechanism
        sasl_options = kwargs.get("kafkaProducerSaslOptions") or {}
        kafkaProducerSaslOptions_mechanism = sasl_options.get("mechanism")
        if kafkaProducerSaslOptions_mechanism is None:
            kafkaProducerSaslOptions_mechanism = "None"
        if kafkaProducerSaslOptions_mechanism not in [
            "None",
            "plain",
            "scram-sha-256",
            "scram-sha-512",
            "aws",
        ]:
            raise ValueError(
                "Unknown kafkaProducerSaslOptions[\"mechanism\"] value: "
                f"{kafkaProducerSaslOptions_mechanism}")
