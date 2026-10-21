from __future__ import annotations

from . import AuthMethod, MonitorType


def _build_monitor_data(
        type: MonitorType,
        name: str,
        parent: int | None = None,
        description: str | None = None,
        conditions: list | None = None,
        interval: int = 60,
        retryInterval: int = 60,
        resendInterval: int = 0,
        maxretries: int = 1,
        upsideDown: bool = False,
        notificationIDList: list | None = None,
        httpBodyEncoding: str = "json",

        # HTTP, KEYWORD, JSON_QUERY, REAL_BROWSER
        url: str | None = None,

        # HTTP, KEYWORD, GRPC_KEYWORD
        maxredirects: int = 10,
        accepted_statuscodes: list[str] | None = None,

        # HTTP, KEYWORD, JSON_QUERY
        expiryNotification: bool = False,
        ignoreTls: bool = False,
        proxyId: int | None = None,
        method: str = "GET",
        body: str | None = None,
        headers: str | None = None,
        authMethod: AuthMethod = AuthMethod.NONE,
        tlsCert: str | None = None,
        tlsKey: str | None = None,
        tlsCa: str | None = None,
        basic_auth_user: str | None = None,
        basic_auth_pass: str | None = None,
        authDomain: str | None = None,
        authWorkstation: str | None = None,
        oauth_auth_method: str = "client_secret_basic",
        oauth_token_url: str | None = None,
        oauth_client_id: str | None = None,
        oauth_client_secret: str | None = None,
        oauth_scopes: str | None = None,
        timeout: int | None = None,

        # KEYWORD
        keyword: str | None = None,
        invertKeyword: bool = False,

        # GRPC_KEYWORD
        grpcUrl: str | None = None,
        grpcEnableTls: bool = False,
        grpcServiceName: str | None = None,
        grpcMethod: str | None = None,
        grpcProtobuf: str | None = None,
        grpcBody: str | None = None,
        grpcMetadata: str | None = None,

        # PORT, PING, DNS, STEAM, MQTT, RADIUS, TAILSCALE_PING
        hostname: str | None = None,

        # PING
        packetSize: int = 56,

        # PORT, DNS, STEAM, MQTT, RADIUS
        port: int | None = None,

        # DNS
        dns_resolve_server: str = "1.1.1.1",
        dns_resolve_type: str = "A",

        # MQTT
        mqttUsername: str = "",
        mqttPassword: str = "",
        mqttTopic: str = "",
        mqttSuccessMessage: str = "",

        # SQLSERVER, POSTGRES, MYSQL, MONGODB, REDIS
        databaseConnectionString: str | None = None,

        # SQLSERVER, POSTGRES, MYSQL
        databaseQuery: str | None = None,

        # DOCKER
        docker_container: str = "",
        docker_host: int | None = None,

        # RADIUS
        radiusUsername: str | None = None,
        radiusPassword: str | None = None,
        radiusSecret: str | None = None,
        radiusCalledStationId: str | None = None,
        radiusCallingStationId: str | None = None,

        # GAMEDIG
        game: str | None = None,
        gamedigGivenPortOnly: bool = True,

        # JSON_QUERY
        jsonPath: str | None = None,
        expectedValue: str | None = None,

        # KAFKA_PRODUCER
        kafkaProducerBrokers: list[str] | None = None,
        kafkaProducerTopic: str | None = None,
        kafkaProducerMessage: str | None = None,
        kafkaProducerSsl: bool = False,
        kafkaProducerAllowAutoTopicCreation: bool = False,
        kafkaProducerSaslOptions: dict | None = None,

        # NTP
        ntpStratumThreshold: int = 5,
        ntpTimeOffsetThreshold: int = 1000,
        ntpRootDispersionThreshold: int = 500,

        # SYSTEM_SERVICE, PM2
        system_service_name: str | None = None,

        # SMTP
        smtpSecurity: str | None = None,

        # MANUAL
        manual_status: int | None = None,

        # WEBSOCKET_UPGRADE
        wsSubprotocol: str = "",
        wsIgnoreSecWebsocketAcceptHeader: bool = False,

        # SNMP
        snmpOid: str | None = None,
        snmpVersion: str = "2c",
        jsonPathOperator: str = "==",

        # SFTP
        sshUsername: str | None = None,
        sshPassword: str | None = None,
        sshPrivateKey: str | None = None,
        sshPassphrase: str | None = None,
        sshAuthMethod: str = "password",
        sftpPath: str | None = None,

        # RABBITMQ
        rabbitmqNodes: list[str] | None = None,
        rabbitmqUsername: str | None = None,
        rabbitmqPassword: str | None = None,

        # GLOBALPING
        subtype: str = "ping",
        location: str = "world",
        protocol: str | None = None,
        ipFamily: str | None = None,
        ping_count: int = 3,
        cacheBust: bool = False,

        # BEARER authentication
        bearer_token: str | None = None,
) -> dict:
    if accepted_statuscodes is None:
        # a websocket check compares the close code, 1000 on success
        accepted_statuscodes = (
            ["1000"] if type == MonitorType.WEBSOCKET_UPGRADE
            else ["200-299"])
    if timeout is None:
        # Kuma's form uses 5 s for SNMP, which is meant for the local network
        timeout = 5 if type == MonitorType.SNMP else 48

    # the server expects an object here, an empty one when unset
    notification_ids = {} if notificationIDList is None else notificationIDList

    data = {
        "type": type,
        "name": name,
        "interval": interval,
        "retryInterval": retryInterval,
        "maxretries": maxretries,
        "notificationIDList": notification_ids,
        "upsideDown": upsideDown,
        "resendInterval": resendInterval,
        "description": description,
        "conditions": conditions,
        "httpBodyEncoding": httpBodyEncoding,
    }

    data.update({
        "parent": parent,
    })

    if type in [MonitorType.KEYWORD, MonitorType.GRPC_KEYWORD]:
        data.update({
            "keyword": keyword,
        })
        data.update({
            "invertKeyword": invertKeyword,
        })

    # HTTP, KEYWORD, JSON_QUERY, REAL_BROWSER
    data.update({
        "url": url,
    })

    # HTTP, KEYWORD, GRPC_KEYWORD
    data.update({
        "maxredirects": maxredirects,
        "accepted_statuscodes": accepted_statuscodes,
    })

    data.update({
        "expiryNotification": expiryNotification,
        "ignoreTls": ignoreTls,
        "proxyId": proxyId,
        "method": method,
        "body": body,
        "headers": headers,
        "authMethod": authMethod,
    })

    data.update({
        "timeout": timeout,
    })

    if authMethod in [AuthMethod.HTTP_BASIC, AuthMethod.NTLM]:
        data.update({
            "basic_auth_user": basic_auth_user,
            "basic_auth_pass": basic_auth_pass,
        })

    if authMethod == AuthMethod.NTLM:
        data.update({
            "authDomain": authDomain,
            "authWorkstation": authWorkstation,
        })

    if authMethod == AuthMethod.BEARER:
        data["bearer_token"] = bearer_token

    if authMethod == AuthMethod.MTLS:
        data.update({
            "tlsCert": tlsCert,
            "tlsKey": tlsKey,
            "tlsCa": tlsCa,
        })

    if authMethod == AuthMethod.OAUTH2_CC:
        data.update({
            "oauth_auth_method": oauth_auth_method,
            "oauth_token_url": oauth_token_url,
            "oauth_client_id": oauth_client_id,
            "oauth_client_secret": oauth_client_secret,
            "oauth_scopes": oauth_scopes,
        })

    # GRPC_KEYWORD
    if type == MonitorType.GRPC_KEYWORD:
        data.update({
            "grpcUrl": grpcUrl,
            "grpcEnableTls": grpcEnableTls,
            "grpcServiceName": grpcServiceName,
            "grpcMethod": grpcMethod,
            "grpcProtobuf": grpcProtobuf,
            "grpcBody": grpcBody,
            "grpcMetadata": grpcMetadata,
        })

    # PORT, PING, DNS, STEAM, MQTT, RADIUS, TAILSCALE_PING
    data.update({
        "hostname": hostname,
    })

    # PING
    data.update({
        "packetSize": packetSize,
    })

    # PORT, DNS, STEAM, MQTT, RADIUS
    if not port:
        if type == MonitorType.DNS:
            port = 53
        elif type == MonitorType.RADIUS:
            port = 1812
        elif type == MonitorType.SNMP:
            port = 161
        elif type == MonitorType.SFTP:
            port = 22
        elif type == MonitorType.GLOBALPING:
            # the port only matters for TCP pings
            port = {"ping": 80, "dns": 53}.get(subtype)
    data.update({
        "port": port,
    })

    # DNS
    data.update({
        "dns_resolve_server": dns_resolve_server,
        "dns_resolve_type": dns_resolve_type,
    })

    # MQTT
    data.update({
        "mqttUsername": mqttUsername,
        "mqttPassword": mqttPassword,
        "mqttTopic": mqttTopic,
        "mqttSuccessMessage": mqttSuccessMessage,
    })

    # SQLSERVER, POSTGRES, MYSQL, MONGODB, REDIS
    data.update({
        "databaseConnectionString": databaseConnectionString
    })

    # SQLSERVER, POSTGRES, MYSQL
    if type in [
        MonitorType.SQLSERVER, MonitorType.POSTGRES, MonitorType.MYSQL,
        MonitorType.ORACLEDB,
    ]:
        data.update({
            "databaseQuery": databaseQuery,
        })

    # DOCKER
    if type == MonitorType.DOCKER:
        data.update({
            "docker_container": docker_container,
            "docker_host": docker_host,
        })

    # RADIUS
    if type == MonitorType.RADIUS:
        data.update({
            "radiusUsername": radiusUsername,
            "radiusPassword": radiusPassword,
            "radiusSecret": radiusSecret,
            "radiusCalledStationId": radiusCalledStationId,
            "radiusCallingStationId": radiusCallingStationId,
        })

    # GAMEDIG
    if type == MonitorType.GAMEDIG:
        data.update({
            "game": game,
        })
        data.update({
            "gamedigGivenPortOnly": gamedigGivenPortOnly,
        })

    # ORACLEDB: the login is separate from the connection string
    if type == MonitorType.ORACLEDB:
        data.update({
            "basic_auth_user": basic_auth_user,
            "basic_auth_pass": basic_auth_pass,
        })

    # WEBSOCKET_UPGRADE
    if type == MonitorType.WEBSOCKET_UPGRADE:
        data.update({
            "wsSubprotocol": wsSubprotocol,
            "wsIgnoreSecWebsocketAcceptHeader": (
                wsIgnoreSecWebsocketAcceptHeader),
        })

    # SNMP: the community string travels in radiusPassword
    if type == MonitorType.SNMP:
        data.update({
            "radiusPassword": radiusPassword,
            "snmpOid": snmpOid,
            # a stored monitor may return null for these: use Kuma's defaults
            "snmpVersion": "2c" if snmpVersion is None else snmpVersion,
            "jsonPath": jsonPath if jsonPath is not None else "$",
            "jsonPathOperator": (
                "==" if jsonPathOperator is None else jsonPathOperator),
            "expectedValue": expectedValue,
        })

    # JSON_QUERY
    if type == MonitorType.JSON_QUERY:
        data.update({
            "jsonPath": jsonPath,
            "expectedValue": expectedValue,
        })

    # KAFKA_PRODUCER
    if type == MonitorType.KAFKA_PRODUCER:
        if kafkaProducerBrokers is None:
            kafkaProducerBrokers = []
        if not kafkaProducerSaslOptions:
            kafkaProducerSaslOptions = {
                "mechanism": "None",
            }
        data.update({
            "kafkaProducerBrokers": kafkaProducerBrokers,
            "kafkaProducerTopic": kafkaProducerTopic,
            "kafkaProducerMessage": kafkaProducerMessage,
            "kafkaProducerSsl": kafkaProducerSsl,
            "kafkaProducerAllowAutoTopicCreation": (
                kafkaProducerAllowAutoTopicCreation),
            "kafkaProducerSaslOptions": kafkaProducerSaslOptions,
        })

    # NTP
    if type == MonitorType.NTP:
        data.update({
            "ntpStratumThreshold": ntpStratumThreshold,
            "ntpTimeOffsetThreshold": ntpTimeOffsetThreshold,
            "ntpRootDispersionThreshold": ntpRootDispersionThreshold,
        })

    # SYSTEM_SERVICE, PM2
    if type in [MonitorType.SYSTEM_SERVICE, MonitorType.PM2]:
        data["system_service_name"] = system_service_name

    # SMTP
    if type == MonitorType.SMTP:
        data["smtpSecurity"] = smtpSecurity

    # MANUAL
    if type == MonitorType.MANUAL:
        data["manual_status"] = manual_status

    # SFTP: only the secret of the chosen method is sent
    if type == MonitorType.SFTP:
        auth = "password" if sshAuthMethod is None else sshAuthMethod
        data.update({
            "sshUsername": sshUsername,
            "sshAuthMethod": auth,
            "sftpPath": sftpPath,
        })
        if auth == "privateKey":
            data["sshPrivateKey"] = sshPrivateKey
            data["sshPassphrase"] = sshPassphrase
        else:
            data["sshPassword"] = sshPassword

    # GLOBALPING: the probe runs from "location", the check is the subtype
    if type == MonitorType.GLOBALPING:
        if protocol is None:
            protocol = {"ping": "ICMP", "dns": "UDP"}.get(subtype)
        data.update({
            "subtype": subtype,
            "location": location,
            "protocol": protocol,
            "ipFamily": ipFamily,
        })
        if subtype == "ping":
            data["ping_count"] = ping_count
        if subtype == "http":
            data.update({
                "cacheBust": cacheBust,
                "keyword": keyword,
                "invertKeyword": invertKeyword,
                "jsonPath": jsonPath if jsonPath is not None else "$",
                "jsonPathOperator": (
                    "==" if jsonPathOperator is None else jsonPathOperator),
                "expectedValue": expectedValue,
            })

    # RABBITMQ
    if type == MonitorType.RABBITMQ:
        data.update({
            "rabbitmqNodes": rabbitmqNodes,
            "rabbitmqUsername": rabbitmqUsername,
            "rabbitmqPassword": rabbitmqPassword,
        })

    return data
