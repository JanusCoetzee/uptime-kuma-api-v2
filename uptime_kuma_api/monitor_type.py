from enum import Enum


class MonitorType(str, Enum):
    """Enumerate monitor types."""

    HTTP = "http"
    """HTTP(s)"""

    KEYWORD = "keyword"
    """HTTP(s) - Keyword"""

    PORT = "port"
    """TCP Port"""

    PING = "ping"
    """Ping"""

    DNS = "dns"
    """DNS"""

    DOCKER = "docker"
    """Docker Container"""

    SYSTEM_SERVICE = "system-service"
    """System Service"""

    PM2 = "pm2"
    """PM2 Process"""

    REAL_BROWSER = "real-browser"
    """HTTP(s) - Browser Engine (Chrome/Chromium)"""

    WEBSOCKET_UPGRADE = "websocket-upgrade"
    """Websocket Upgrade"""

    SFTP = "sftp"
    """SFTP"""

    GROUP = "group"
    """Group"""

    PUSH = "push"
    """Push"""

    MANUAL = "manual"
    """Manual"""

    GLOBALPING = "globalping"
    """Globalping - Access global monitoring probes"""

    GRPC_KEYWORD = "grpc-keyword"
    """gRPC(s) - Keyword"""

    JSON_QUERY = "json-query"
    """HTTP(s) - Json Query"""

    KAFKA_PRODUCER = "kafka-producer"
    """Kafka Producer"""

    MQTT = "mqtt"
    """MQTT"""

    NTP = "ntp"
    """NTP"""

    RABBITMQ = "rabbitmq"
    """RabbitMQ"""

    SIP_OPTIONS = "sip-options"
    """SIP Options Ping"""

    SMTP = "smtp"
    """SMTP"""

    SNMP = "snmp"
    """SNMP"""

    TAILSCALE_PING = "tailscale-ping"
    """Tailscale Ping"""

    SQLSERVER = "sqlserver"
    """Microsoft SQL Server"""

    MONGODB = "mongodb"
    """MongoDB"""

    MYSQL = "mysql"
    """MySQL/MariaDB"""

    ORACLEDB = "oracledb"
    """Oracle Database"""

    POSTGRES = "postgres"
    """PostgreSQL"""

    RADIUS = "radius"
    """Radius"""

    REDIS = "redis"
    """Redis"""

    GAMEDIG = "gamedig"
    """GameDig"""

    STEAM = "steam"
    """Steam Game Server"""
