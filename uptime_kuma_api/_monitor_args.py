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


# In MonitorType (generated from Kuma 2.5.6) but without argument checks or
# payload fields yet; add_monitor/edit_monitor reject them (#118).
UNSUPPORTED_MONITOR_TYPES = frozenset({
    MonitorType.WEBSOCKET_UPGRADE,
    MonitorType.SFTP,
    MonitorType.GLOBALPING,
    MonitorType.RABBITMQ,
    MonitorType.SNMP,
    MonitorType.ORACLEDB,
})


def parse_monitor_type(data) -> None:
    parse_value(data, "type", MonitorType)


def parse_auth_method(data) -> None:
    parse_value(data, "authMethod", AuthMethod, AuthMethod.NONE)


def gen_secret(length: int) -> str:
    chars = string.ascii_uppercase + string.ascii_lowercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def _convert_monitor_return(monitor) -> None:
    if isinstance(monitor["notificationIDList"], dict):
        monitor["notificationIDList"] = [int(i) for i in monitor["notificationIDList"].keys()]


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
        MonitorType.GRPC_KEYWORD: ["grpcUrl", "keyword", "grpcServiceName", "grpcMethod"],
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
        MonitorType.RADIUS: ["radiusUsername", "radiusPassword", "radiusSecret", "radiusCalledStationId", "radiusCallingStationId"],
        MonitorType.REDIS: ["databaseConnectionString"],
        MonitorType.GROUP: [],
        MonitorType.JSON_QUERY: ["url", "jsonPath", "expectedValue"],
        MonitorType.REAL_BROWSER: ["url"],
        MonitorType.KAFKA_PRODUCER: ["kafkaProducerTopic", "kafkaProducerMessage"],
        MonitorType.TAILSCALE_PING: ["hostname"],
        MonitorType.NTP: ["hostname"],
        MonitorType.SYSTEM_SERVICE: ["system_service_name"],
        MonitorType.PM2: ["system_service_name"],
        MonitorType.MANUAL: [],
        MonitorType.SIP_OPTIONS: ["hostname", "port"],
        MonitorType.SMTP: ["hostname", "port"],
    }
    type_ = kwargs["type"]
    if type_ in UNSUPPORTED_MONITOR_TYPES:
        raise ValueError(f"monitor type {getattr(type_, "value", type_)!r} is not supported yet (#118)")
    if type_ not in required_args_by_type:
        raise ValueError(f"unsupported monitor type: {type_}")
    required_args = required_args_by_type[type_]
    _check_missing_arguments(required_args, kwargs)

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
        if accepted_statuscode not in allowed_accepted_statuscodes:
            raise ValueError(f"Unknown accepted_statuscodes value: {accepted_statuscode!r}, expected 'NNN' (100-999) or 'N00-N99' (for example '200-299')")

    dns_resolve_type = kwargs["dns_resolve_type"]
    if dns_resolve_type not in [
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

    if type_ == MonitorType.MANUAL:
        manual_status = kwargs.get("manual_status")
        if manual_status not in (None, 0, 1):
            raise ValueError(
                f"Unknown manual_status value: {manual_status!r}, "
                "expected 0 (down) or 1 (up)")

    if type_ == MonitorType.KAFKA_PRODUCER:
        # a missing or None option means the server default mechanism
        kafkaProducerSaslOptions_mechanism = (kwargs.get("kafkaProducerSaslOptions") or {}).get("mechanism")
        if kafkaProducerSaslOptions_mechanism is None:
            kafkaProducerSaslOptions_mechanism = "None"
        if kafkaProducerSaslOptions_mechanism not in [
            "None",
            "plain",
            "scram-sha-256",
            "scram-sha-512",
            "aws",
        ]:
            raise ValueError(f"Unknown kafkaProducerSaslOptions[\"mechanism\"] value: {kafkaProducerSaslOptions_mechanism}")
