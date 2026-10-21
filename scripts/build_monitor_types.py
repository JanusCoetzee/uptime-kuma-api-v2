from bs4 import BeautifulSoup

from utils import KUMA_SRC, parse_vue_template, require_titles, write_to_file


titles = {
    "http": "HTTP(s)",
    "port": "TCP Port",
    "ping": "Ping",
    "keyword": "HTTP(s) - Keyword",
    "grpc-keyword": "gRPC(s) - Keyword",
    "dns": "DNS",
    "docker": "Docker Container",
    "push": "Push",
    "steam": "Steam Game Server",
    "gamedig": "GameDig",
    "mqtt": "MQTT",
    "sqlserver": "Microsoft SQL Server",
    "postgres": "PostgreSQL",
    "mysql": "MySQL/MariaDB",
    "mongodb": "MongoDB",
    "radius": "Radius",
    "redis": "Redis",
    "group": "Group",
    "json-query": "HTTP(s) - Json Query",
    "real-browser": "HTTP(s) - Browser Engine (Chrome/Chromium)",
    "kafka-producer": "Kafka Producer",
    "tailscale-ping": "Tailscale Ping",
    "system-service": "System Service",
    "pm2": "PM2 Process",
    "websocket-upgrade": "Websocket Upgrade",
    "sftp": "SFTP",
    "manual": "Manual",
    "globalping": "Globalping - Access global monitoring probes",
    "ntp": "NTP",
    "rabbitmq": "RabbitMQ",
    "sip-options": "SIP Options Ping",
    "smtp": "SMTP",
    "snmp": "SNMP",
    "oracledb": "Oracle Database",
}


def parse_monitor_types():
    content = parse_vue_template(KUMA_SRC / "src/pages/EditMonitor.vue")

    soup = BeautifulSoup(content, "html.parser")
    select = soup.find("select", id="type")
    options = select.find_all("option")

    values = list(dict.fromkeys(o.attrs["value"] for o in options))
    require_titles("monitor types", values, titles, "build_monitor_types.py")

    types = {}
    for type_ in values:
        types[type_] = {
            "value": type_,
            "title": titles[type_]
        }
    return types


monitor_types = parse_monitor_types()

write_to_file(
    "monitor_type.py.j2", "uptime_kuma_client/monitor_type.py",
    monitor_types=monitor_types
)
