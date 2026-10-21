RAISES = (
    ":raises TypeError: If a required argument is missing or an argument "
    "is unknown.\n"
    ":raises ValueError: If an argument value is invalid."
)


def append_docstring(value, validated=True):
    def _doc(func):
        # inserts the value into the existing docstring before the :return: line
        split_value = ":return:"
        splitted = func.__doc__.split(split_value)
        part1 = splitted[0]
        line = [i for i in part1.split("\n") if i][0]
        indent = len(line) - len(line.lstrip())
        line_start = " " * indent
        part2 = split_value + line_start.join(splitted[1:])
        text = value
        if validated:
            text += "\n" + line_start + RAISES.replace("\n", "\n" + line_start)
        func.__doc__ = part1 + "\n" + line_start + text + "\n" + line_start + part2
        return func

    return _doc


def monitor_docstring(mode) -> str:
    return f"""
        :param MonitorType{", optional" if mode == "edit" else ""} type: Monitor Type
        :param str{", optional" if mode == "edit" else ""} name: Friendly Name
        :param str, optional parent: Id of the monitor group, defaults to None
        :param str, optional description: Description, defaults to None
        :param int, optional interval: Heartbeat Interval, defaults to 60
        :param int, optional retryInterval: Retry every X seconds, defaults to 60
        :param int, optional resendInterval: Resend every X times, defaults to 0
        :param int, optional maxretries: Retries. Maximum retries before the service is marked as down and a notification is sent., defaults to 0
        :param bool, optional upsideDown: Upside Down Mode. Flip the status upside down. If the service is reachable, it is DOWN., defaults to False
        :param list, optional notificationIDList: Notifications, defaults to None
        :param str, optional url: URL, defaults to None
        :param bool, optional expiryNotification: Certificate Expiry Notification, defaults to False
        :param bool, optional ignoreTls: Ignore TLS/SSL error for HTTPS websites, defaults to False
        :param int, optional maxredirects: Max. Redirects. Maximum number of redirects to follow. Set to 0 to disable redirects., defaults to 10
        :param list, optional accepted_statuscodes: Accepted Status Codes. Select status codes which are considered as a successful response., defaults to None
        :param int, optional proxyId: Proxy, defaults to None
        :param str, optional method: Method, defaults to "GET"
        :param str, optional httpBodyEncoding: Body Encoding, defaults to "json". Allowed values: "json", "xml".
        :param str, optional body: Body, defaults to None
        :param str, optional headers: Headers, defaults to None
        :param AuthMethod, optional authMethod: Method, defaults to :attr:`~.AuthMethod.NONE`
        :param str, optional tlsCert: Cert for ``authMethod`` :attr:`~.AuthMethod.MTLS`, defaults to None.
        :param str, optional tlsKey: Key for ``authMethod`` :attr:`~.AuthMethod.MTLS`, defaults to None.
        :param str, optional tlsCa: Ca for ``authMethod`` :attr:`~.AuthMethod.MTLS`, defaults to None.
        :param str, optional basic_auth_user: Username for ``authMethod`` :attr:`~.AuthMethod.HTTP_BASIC` and :attr:`~.AuthMethod.NTLM`, defaults to None
        :param str, optional basic_auth_pass: Password for ``authMethod`` :attr:`~.AuthMethod.HTTP_BASIC` and :attr:`~.AuthMethod.NTLM`, defaults to None
        :param str, optional authDomain: Domain for ``authMethod`` :attr:`~.AuthMethod.NTLM`, defaults to None
        :param str, optional authWorkstation: Workstation for ``authMethod`` :attr:`~.AuthMethod.NTLM`, defaults to None
        :param str, optional oauth_auth_method: Authentication Method, defaults to None
        :param str, optional oauth_token_url: OAuth Token URL, defaults to None
        :param str, optional oauth_client_id: Client ID, defaults to None
        :param str, optional oauth_client_secret: Client Secret, defaults to None
        :param str, optional oauth_scopes: OAuth Scope, defaults to None
        :param int, optional timeout: Request Timeout, defaults to None
        :param str, optional keyword: Keyword. Search keyword in plain HTML or JSON response. The search is case-sensitive., defaults to None
        :param bool, optional invertKeyword: Invert Keyword. Look for the keyword to be absent rather than present., defaults to False
        :param str, optional hostname: Hostname, defaults to None
        :param int, optional packetSize: Packet Size, defaults to None
        :param int, optional port: Port, ``type`` :attr:`~.MonitorType.DNS` defaults to ``53`` and ``type`` :attr:`~.MonitorType.RADIUS` defaults to ``1812``
        :param str, optional dns_resolve_server: Resolver Server, defaults to "1.1.1.1"
        :param str, optional dns_resolve_type: Resource Record Type, defaults to "A". Available values are:

            - "A"
            - "AAAA"
            - "CAA"
            - "CNAME"
            - "MX"
            - "NS"
            - "PTR"
            - "SOA"
            - "SRV"
            - "TXT"
        :param str, optional mqttUsername: MQTT Username, defaults to None
        :param str, optional mqttPassword: MQTT Password, defaults to None
        :param str, optional mqttTopic: MQTT Topic, defaults to None
        :param str, optional mqttSuccessMessage: MQTT Success Message, defaults to None
        :param str, optional databaseConnectionString: Connection String, defaults to None
        :param str, optional databaseQuery: Query, defaults to None
        :param str, optional docker_container: Container Name / ID, defaults to ""
        :param int, optional docker_host: Docker Host, defaults to None
        :param str, optional radiusUsername: Radius Username, defaults to None
        :param str, optional radiusPassword: Radius Password. For SNMP this is the community string., defaults to None
        :param str, optional radiusSecret: Radius Secret. Shared Secret between client and server., defaults to None
        :param str, optional radiusCalledStationId: Called Station Id. Identifier of the called device., defaults to None
        :param str, optional radiusCallingStationId: Calling Station Id. Identifier of the calling device., defaults to None
        :param str, optional game: Game, defaults to None
        :param bool, optional gamedigGivenPortOnly: Gamedig: Guess Port. The port used by Valve Server Query Protocol may be different from the client port. Try this if the monitor cannot connect to your server., defaults to False
        :param str, optional jsonPath: Json Query, defaults to None
        :param str, optional expectedValue: Expected Value, defaults to None
        :param str, optional kafkaProducerBrokers: Kafka Broker list, defaults to None
        :param str, optional kafkaProducerTopic: Kafka Topic Name, defaults to None
        :param str, optional kafkaProducerMessage: Kafka Producer Message, defaults to None
        :param bool, optional kafkaProducerSsl: Enable Kafka SSL, defaults to False
        :param bool, optional kafkaProducerAllowAutoTopicCreation: Enable Kafka Producer Auto Topic Creation, defaults to False
        :param dict, optional kafkaProducerSaslOptions: Kafka SASL Options

            - **mechanism** (*str*, *optional*): Mechanism, defaults to "None". Available values are:

                - "None"
                - "plain"
                - "scram-sha-256"
                - "scram-sha-512"
                - "aws"
            - **username** (*str*, *optional*): Username, defaults to None
            - **password** (*str*, *optional*): Password, defaults to None
            - **authorizationIdentity** (*str*, *optional*): Authorization Identity, defaults to None
            - **accessKeyId** (*str*, *optional*): AccessKey Id, defaults to None
            - **secretAccessKey** (*str*, *optional*): Secret AccessKey, defaults to None
            - **sessionToken** (*str*, *optional*): Session Token, defaults to None
        :param int, optional ntpStratumThreshold: NTP only. Maximum acceptable stratum; the monitor is down at or above it (1-15), defaults to 5
        :param int, optional ntpTimeOffsetThreshold: NTP only. Maximum acceptable clock offset in milliseconds, defaults to 1000
        :param int, optional ntpRootDispersionThreshold: NTP only. Maximum acceptable root dispersion in milliseconds, defaults to 500
        :param str, optional system_service_name: SYSTEM_SERVICE and PM2 only. Name of the system service, or of the pm2 process. Required for those types., defaults to None
        :param str, optional smtpSecurity: SMTP only. "secure" (SMTPS), "starttls" (require STARTTLS) or "nostarttls" (ignore STARTTLS), defaults to None (server default)
        :param str, optional wsSubprotocol: WEBSOCKET_UPGRADE only. Comma separated subprotocols to request, defaults to ""
        :param bool, optional wsIgnoreSecWebsocketAcceptHeader: WEBSOCKET_UPGRADE only. Ignore the ``Sec-WebSocket-Accept`` header of the response, defaults to False
        :param str, optional snmpOid: SNMP only. OID to query, for example ``1.3.6.1.2.1.1.3.0``. Required for that type., defaults to None
        :param str, optional snmpVersion: SNMP only. ``1`` or ``2c``; ``3`` is not usable on Kuma 2.5.6 because the server does not save the username, defaults to "2c"
        :param str, optional jsonPathOperator: SNMP only. Comparison of the value found at ``jsonPath`` with ``expectedValue``: ``>``, ``>=``, ``<``, ``<=``, ``!=``, ``==`` or ``contains``, defaults to "=="
        :param str, optional sshUsername: SFTP only. SSH user name. Required for that type., defaults to None
        :param str, optional sshAuthMethod: SFTP only. ``password`` or ``privateKey``, defaults to "password"
        :param str, optional sshPassword: SFTP only. Password, required for ``sshAuthMethod="password"`` and not sent by add_monitor otherwise. edit_monitor sends the stored value of the other method back unchanged., defaults to None
        :param str, optional sshPrivateKey: SFTP only. Private key, required for ``sshAuthMethod="privateKey"`` and not sent by add_monitor otherwise. edit_monitor sends the stored value of the other method back unchanged., defaults to None
        :param str, optional sshPassphrase: SFTP only. Passphrase of the private key, defaults to None
        :param str, optional sftpPath: SFTP only. Path that must exist on the server, defaults to None
        :param list, optional rabbitmqNodes: RABBITMQ only. Base URLs (``http://`` or ``https://``) of the management API of the nodes. At least one is required for that type., defaults to None
        :param str, optional rabbitmqUsername: RABBITMQ only. Required for that type., defaults to None
        :param str, optional rabbitmqPassword: RABBITMQ only. Required for that type., defaults to None
        :param str, optional subtype: GLOBALPING only. ``ping``, ``http`` or ``dns``, defaults to "ping". ``ping`` needs ``hostname``, ``http`` needs ``url`` (``method`` HEAD, GET or OPTIONS) and ``dns`` needs ``hostname`` (``dns_resolve_type`` may also be ANY, DNSKEY, DS, HTTPS, NSEC, RRSIG or SVCB)
        :param str, optional location: GLOBALPING only. One Globalping location, for example ``world``, ``germany`` or ``amazon+germany``, defaults to "world"
        :param str, optional protocol: GLOBALPING only. ``ICMP`` or ``TCP`` for ping, ``UDP`` or ``TCP`` for dns, ``HTTP2`` for http (None selects it from the URL). Defaults to ``ICMP`` for ping, ``UDP`` for dns and None for http
        :param str, optional ipFamily: GLOBALPING only. ``ipv4`` or ``ipv6``, None selects it automatically, defaults to None
        :param int, optional ping_count: GLOBALPING ping only. Number of echo requests, 1 to 100, defaults to 3
        :param bool, optional cacheBust: GLOBALPING http only. Adds a random query parameter to every request, defaults to False
        :param str, optional bearer_token: Token for ``authMethod=AuthMethod.BEARER``, which requires it., defaults to None
        :param int, optional manual_status: MANUAL only. 1 sets the monitor up, 0 sets it down; it stays pending when not set. The server does not return this value; editing without it keeps the current one., defaults to None
    """


def notification_docstring(mode) -> str:
    return f"""
        :param str{", optional" if mode == "edit" else ""} name: Friendly Name
        :param NotificationType{", optional" if mode == "edit" else ""} type: Notification Type
        :param bool, optional isDefault: Default enabled. This notification will be enabled by default for new monitors. You can still disable the notification separately for each monitor., defaults to False
        :param bool, optional applyExisting: Apply on all existing monitors, defaults to False

        :param str Whatsapp360messengerAuthToken: Notification option for ``type`` :attr:`~.NotificationType.WHATSAPP360MESSENGER`.
        :param bool, optional Whatsapp360messengerUseTemplate: Notification option for ``type`` :attr:`~.NotificationType.WHATSAPP360MESSENGER`.
        :param str, optional Whatsapp360messengerTemplate: Notification option for ``type`` :attr:`~.NotificationType.WHATSAPP360MESSENGER`.
        :param str, optional Whatsapp360messengerRecipient: Notification option for ``type`` :attr:`~.NotificationType.WHATSAPP360MESSENGER`.
        :param str, optional Whatsapp360messengerGroupIds: Notification option for ``type`` :attr:`~.NotificationType.WHATSAPP360MESSENGER`.
        :param str elksFromNumber: Notification option for ``type`` :attr:`~.NotificationType.ELKS`.
        :param str elksToNumber: Notification option for ``type`` :attr:`~.NotificationType.ELKS`.
        :param str elksUsername: Notification option for ``type`` :attr:`~.NotificationType.ELKS`.
        :param str elksAuthToken: Notification option for ``type`` :attr:`~.NotificationType.ELKS`.
        :param str, optional haloUsername: Notification option for ``type`` :attr:`~.NotificationType.HALOPSA`.
        :param str, optional haloPassword: Notification option for ``type`` :attr:`~.NotificationType.HALOPSA`.
        :param str halowebhookurl: Notification option for ``type`` :attr:`~.NotificationType.HALOPSA`.
        :param str alertaApiKey: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`.
        :param str alertaEnvironment: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`.
        :param str alertaApiEndpoint: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`.
        :param str alertaAlertState: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`.
        :param str alertaRecoverState: Notification option for ``type`` :attr:`~.NotificationType.ALERTA`.
        :param str alertNowWebhookURL: Notification option for ``type`` :attr:`~.NotificationType.ALERTNOW`.
        :param bool, optional optionalParameters: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str phonenumber: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str templateCode: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str signName: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str accessKeyId: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str secretAccessKey: Notification option for ``type`` :attr:`~.NotificationType.ALIYUNSMS`.
        :param str amootMobiles: Notification option for ``type`` :attr:`~.NotificationType.AMOOTSMS`.
        :param str amootApiToken: Notification option for ``type`` :attr:`~.NotificationType.AMOOTSMS`.
        :param bool, optional amootUsePattern: Notification option for ``type`` :attr:`~.NotificationType.AMOOTSMS`.
        :param int, optional amootPatternCodeId: Notification option for ``type`` :attr:`~.NotificationType.AMOOTSMS`.
        :param bool, optional amootUseOwnLine: Notification option for ``type`` :attr:`~.NotificationType.AMOOTSMS`.
        :param str, optional amootLineNumber: Notification option for ``type`` :attr:`~.NotificationType.AMOOTSMS`.
        :param str appriseURL: Notification option for ``type`` :attr:`~.NotificationType.APPRISE`.
        :param str, optional title: Notification option for ``type`` :attr:`~.NotificationType.APPRISE`.
        :param str baleBotToken: Notification option for ``type`` :attr:`~.NotificationType.BALE`.
        :param str baleChatID: Notification option for ``type`` :attr:`~.NotificationType.BALE`.
        :param str barkEndpoint: Notification option for ``type`` :attr:`~.NotificationType.BARK`.
        :param str barkGroup: Notification option for ``type`` :attr:`~.NotificationType.BARK`.
        :param str barkSound: Notification option for ``type`` :attr:`~.NotificationType.BARK`.
        :param str apiVersion: Notification option for ``type`` :attr:`~.NotificationType.BARK`.
        :param str bearsmsUsername: Notification option for ``type`` :attr:`~.NotificationType.BEARSMS`.
        :param str bearsmsHashKey: Notification option for ``type`` :attr:`~.NotificationType.BEARSMS`.
        :param str bearsmsPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.BEARSMS`.
        :param str, optional bearsmsSenderId: Notification option for ``type`` :attr:`~.NotificationType.BEARSMS`.
        :param str bitrix24UserID: Notification option for ``type`` :attr:`~.NotificationType.BITRIX24`.
        :param str bitrix24WebhookURL: Notification option for ``type`` :attr:`~.NotificationType.BITRIX24`.
        :param str brevoApiKey: Notification option for ``type`` :attr:`~.NotificationType.BREVO`.
        :param str brevoToEmail: Notification option for ``type`` :attr:`~.NotificationType.BREVO`.
        :param str brevoFromEmail: Notification option for ``type`` :attr:`~.NotificationType.BREVO`.
        :param str, optional brevoFromName: Notification option for ``type`` :attr:`~.NotificationType.BREVO`.
        :param str, optional brevoSubject: Notification option for ``type`` :attr:`~.NotificationType.BREVO`.
        :param str, optional brevoCcEmail: Notification option for ``type`` :attr:`~.NotificationType.BREVO`.
        :param str, optional brevoBccEmail: Notification option for ``type`` :attr:`~.NotificationType.BREVO`.
        :param str callMeBotEndpoint: Notification option for ``type`` :attr:`~.NotificationType.CALLMEBOT`.
        :param str cellsyntLogin: Notification option for ``type`` :attr:`~.NotificationType.CELLSYNT`.
        :param str cellsyntPassword: Notification option for ``type`` :attr:`~.NotificationType.CELLSYNT`.
        :param str cellsyntDestination: Notification option for ``type`` :attr:`~.NotificationType.CELLSYNT`.
        :param str cellsyntOriginatortype: Notification option for ``type`` :attr:`~.NotificationType.CELLSYNT`.
        :param int, optional cellsyntOriginator: Notification option for ``type`` :attr:`~.NotificationType.CELLSYNT`.
        :param bool, optional cellsyntAllowLongSMS: Notification option for ``type`` :attr:`~.NotificationType.CELLSYNT`.
        :param str clicksendsmsLogin: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`.
        :param str clicksendsmsPassword: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`.
        :param str clicksendsmsToNumber: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`.
        :param str, optional clicksendsmsSenderName: Notification option for ``type`` :attr:`~.NotificationType.CLICKSENDSMS`.
        :param str clickupToken: Notification option for ``type`` :attr:`~.NotificationType.CLICKUP`.
        :param bool, optional clickupDisableUrl: Notification option for ``type`` :attr:`~.NotificationType.CLICKUP`.
        :param str clickupWorkspaceId: Notification option for ``type`` :attr:`~.NotificationType.CLICKUP`.
        :param str clickupChannelId: Notification option for ``type`` :attr:`~.NotificationType.CLICKUP`.
        :param str mentioning: Notification option for ``type`` :attr:`~.NotificationType.DINGDING`.
        :param str, optional mobileList: Notification option for ``type`` :attr:`~.NotificationType.DINGDING`.
        :param str, optional userList: Notification option for ``type`` :attr:`~.NotificationType.DINGDING`.
        :param str webHookUrl: Notification option for ``type`` :attr:`~.NotificationType.DINGDING`.
        :param str secretKey: Notification option for ``type`` :attr:`~.NotificationType.DINGDING`.
        :param str, optional discordUsername: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str discordWebhookUrl: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str, optional discordChannelType: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str, optional threadId: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str, optional discordMessageFormat: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str, optional discordMessageTemplate: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str, optional postName: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param bool, optional discordSuppressNotifications: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param bool, optional disableUrl: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str, optional discordPrefixMessage: Notification option for ``type`` :attr:`~.NotificationType.DISCORD`.
        :param str egosmsPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.EGOSMS`.
        :param str egosmsUsername: Notification option for ``type`` :attr:`~.NotificationType.EGOSMS`.
        :param str egosmsPassword: Notification option for ``type`` :attr:`~.NotificationType.EGOSMS`.
        :param str, optional egosmsSender: Notification option for ``type`` :attr:`~.NotificationType.EGOSMS`.
        :param str evolutionAuthToken: Notification option for ``type`` :attr:`~.NotificationType.EVOLUTION`.
        :param str, optional evolutionCustomMessage: Notification option for ``type`` :attr:`~.NotificationType.EVOLUTION`.
        :param bool, optional evolutionUseCustomMessage: Notification option for ``type`` :attr:`~.NotificationType.EVOLUTION`.
        :param str evolutionRecipient: Notification option for ``type`` :attr:`~.NotificationType.EVOLUTION`.
        :param str, optional evolutionApiUrl: Notification option for ``type`` :attr:`~.NotificationType.EVOLUTION`.
        :param str evolutionInstanceName: Notification option for ``type`` :attr:`~.NotificationType.EVOLUTION`.
        :param str feishuWebHookUrl: Notification option for ``type`` :attr:`~.NotificationType.FEISHU`.
        :param str flashdutySeverity: Notification option for ``type`` :attr:`~.NotificationType.FLASHDUTY`.
        :param str, optional flashdutyIntegrationKey: Notification option for ``type`` :attr:`~.NotificationType.FLASHDUTY`.
        :param str, optional flowtriqApiKey: Notification option for ``type`` :attr:`~.NotificationType.FLOWTRIQ`.
        :param str flowtriqWebhookUrl: Notification option for ``type`` :attr:`~.NotificationType.FLOWTRIQ`.
        :param str, optional fluxerUsername: Notification option for ``type`` :attr:`~.NotificationType.FLUXER`.
        :param str fluxerWebhookUrl: Notification option for ``type`` :attr:`~.NotificationType.FLUXER`.
        :param str, optional fluxerMessageFormat: Notification option for ``type`` :attr:`~.NotificationType.FLUXER`.
        :param str, optional fluxerMessageTemplate: Notification option for ``type`` :attr:`~.NotificationType.FLUXER`.
        :param bool, optional disableUrl: Notification option for ``type`` :attr:`~.NotificationType.FLUXER`.
        :param str, optional fluxerPrefixMessage: Notification option for ``type`` :attr:`~.NotificationType.FLUXER`.
        :param str freemobileUser: Notification option for ``type`` :attr:`~.NotificationType.FREEMOBILE`.
        :param str freemobilePass: Notification option for ``type`` :attr:`~.NotificationType.FREEMOBILE`.
        :param str goAlertBaseURL: Notification option for ``type`` :attr:`~.NotificationType.GOALERT`.
        :param str goAlertToken: Notification option for ``type`` :attr:`~.NotificationType.GOALERT`.
        :param int googleChatMaxRetries: Notification option for ``type`` :attr:`~.NotificationType.GOOGLECHAT`.
        :param bool, optional googleChatUseTemplate: Notification option for ``type`` :attr:`~.NotificationType.GOOGLECHAT`.
        :param str, optional googleChatTemplate: Notification option for ``type`` :attr:`~.NotificationType.GOOGLECHAT`.
        :param str googleChatWebhookURL: Notification option for ``type`` :attr:`~.NotificationType.GOOGLECHAT`.
        :param str googleSheetsWebhookUrl: Notification option for ``type`` :attr:`~.NotificationType.GOOGLESHEETS`.
        :param str gorushDeviceToken: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str, optional gorushPlatform: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str, optional gorushTitle: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str, optional gorushPriority: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param int, optional gorushRetry: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str, optional gorushTopic: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str gorushServerURL: Notification option for ``type`` :attr:`~.NotificationType.GORUSH`.
        :param str gotifyserverurl: Notification option for ``type`` :attr:`~.NotificationType.GOTIFY`.
        :param str gotifyapplicationToken: Notification option for ``type`` :attr:`~.NotificationType.GOTIFY`.
        :param int gotifyPriority: Notification option for ``type`` :attr:`~.NotificationType.GOTIFY`.
        :param str GrafanaOncallURL: Notification option for ``type`` :attr:`~.NotificationType.GRAFANAONCALL`.
        :param str gtxMessagingFrom: Notification option for ``type`` :attr:`~.NotificationType.GTXMESSAGING`.
        :param str gtxMessagingTo: Notification option for ``type`` :attr:`~.NotificationType.GTXMESSAGING`.
        :param str gtxMessagingApiKey: Notification option for ``type`` :attr:`~.NotificationType.GTXMESSAGING`.
        :param str heiiOnCallApiKey: Notification option for ``type`` :attr:`~.NotificationType.HEIIONCALL`.
        :param str heiiOnCallTriggerId: Notification option for ``type`` :attr:`~.NotificationType.HEIIONCALL`.
        :param str, optional notificationService: Notification option for ``type`` :attr:`~.NotificationType.HOMEASSISTANT`.
        :param str longLivedAccessToken: Notification option for ``type`` :attr:`~.NotificationType.HOMEASSISTANT`.
        :param str homeAssistantUrl: Notification option for ``type`` :attr:`~.NotificationType.HOMEASSISTANT`.
        :param int, optional jsmPriority: Notification option for ``type`` :attr:`~.NotificationType.JIRASERVICEMANAGEMENT`.
        :param str jsmCloudId: Notification option for ``type`` :attr:`~.NotificationType.JIRASERVICEMANAGEMENT`.
        :param str jsmEmail: Notification option for ``type`` :attr:`~.NotificationType.JIRASERVICEMANAGEMENT`.
        :param str jsmApiToken: Notification option for ``type`` :attr:`~.NotificationType.JIRASERVICEMANAGEMENT`.
        :param str webhookAPIKey: Notification option for ``type`` :attr:`~.NotificationType.KEEP`.
        :param str webhookURL: Notification option for ``type`` :attr:`~.NotificationType.KEEP`.
        :param str kookGuildID: Notification option for ``type`` :attr:`~.NotificationType.KOOK`.
        :param str kookBotToken: Notification option for ``type`` :attr:`~.NotificationType.KOOK`.
        :param str lineChannelAccessToken: Notification option for ``type`` :attr:`~.NotificationType.LINE`.
        :param str lineUserID: Notification option for ``type`` :attr:`~.NotificationType.LINE`.
        :param str lunaseaTarget: Notification option for ``type`` :attr:`~.NotificationType.LUNASEA`. Allowed values: "device", "user".
        :param str, optional lunaseaUserID: Notification option for ``type`` :attr:`~.NotificationType.LUNASEA`. User ID.
        :param str, optional lunaseaDevice: Notification option for ``type`` :attr:`~.NotificationType.LUNASEA`. Device ID.
        :param str internalRoomId: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`.
        :param str accessToken: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`.
        :param bool, optional matrixUseTemplate: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`.
        :param str, optional matrixTemplate: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`.
        :param str homeserverUrl: Notification option for ``type`` :attr:`~.NotificationType.MATRIX`.
        :param str, optional mattermostusername: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`.
        :param str mattermostWebhookUrl: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`.
        :param str, optional mattermostchannel: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`.
        :param str, optional mattermosticonemo: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`.
        :param str, optional mattermosticonurl: Notification option for ``type`` :attr:`~.NotificationType.MATTERMOST`.
        :param str maxApiUrl: Notification option for ``type`` :attr:`~.NotificationType.MAX`.
        :param str maxChatID: Notification option for ``type`` :attr:`~.NotificationType.MAX`.
        :param str maxBotToken: Notification option for ``type`` :attr:`~.NotificationType.MAX`.
        :param bool, optional maxUseTemplate: Notification option for ``type`` :attr:`~.NotificationType.MAX`.
        :param str, optional maxTemplate: Notification option for ``type`` :attr:`~.NotificationType.MAX`.
        :param str, optional maxTemplateFormat: Notification option for ``type`` :attr:`~.NotificationType.MAX`.
        :param str httpAddr: Notification option for ``type`` :attr:`~.NotificationType.MILKY`.
        :param str, optional msgType: Notification option for ``type`` :attr:`~.NotificationType.MILKY`.
        :param str accessToken: Notification option for ``type`` :attr:`~.NotificationType.MILKY`.
        :param str recieverId: Notification option for ``type`` :attr:`~.NotificationType.MILKY`.
        :param str botSecret: Notification option for ``type`` :attr:`~.NotificationType.NEXTCLOUDTALK`.
        :param bool, optional sendSilentUp: Notification option for ``type`` :attr:`~.NotificationType.NEXTCLOUDTALK`.
        :param bool, optional sendSilentDown: Notification option for ``type`` :attr:`~.NotificationType.NEXTCLOUDTALK`.
        :param str, optional host: Notification option for ``type`` :attr:`~.NotificationType.NEXTCLOUDTALK`.
        :param str, optional conversationToken: Notification option for ``type`` :attr:`~.NotificationType.NEXTCLOUDTALK`.
        :param str sender: Notification option for ``type`` :attr:`~.NotificationType.NOSTR`.
        :param str recipients: Notification option for ``type`` :attr:`~.NotificationType.NOSTR`.
        :param str relays: Notification option for ``type`` :attr:`~.NotificationType.NOSTR`.
        :param str, optional notiferyTitle: Notification option for ``type`` :attr:`~.NotificationType.NOTIFERY`.
        :param str, optional notiferyGroup: Notification option for ``type`` :attr:`~.NotificationType.NOTIFERY`.
        :param str notiferyApiKey: Notification option for ``type`` :attr:`~.NotificationType.NOTIFERY`.
        :param str, optional notifyAppIconUrl: Notification option for ``type`` :attr:`~.NotificationType.NOTIFYAPP`.
        :param str notifyAppDeviceId: Notification option for ``type`` :attr:`~.NotificationType.NOTIFYAPP`.
        :param str notifyAppToken: Notification option for ``type`` :attr:`~.NotificationType.NOTIFYAPP`.
        :param str, optional ntfyAuthenticationMethod: Notification option for ``type`` :attr:`~.NotificationType.NTFY`. Authentication Method.
        :param str, optional ntfyusername: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str, optional ntfypassword: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str, optional ntfyaccesstoken: Notification option for ``type`` :attr:`~.NotificationType.NTFY`. Access Token.
        :param str, optional ntfyCall: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str ntfytopic: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param bool, optional ntfyUseTemplate: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str, optional ntfyCustomTitle: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str, optional ntfyCustomMessage: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param int ntfyPriority: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str ntfyserverurl: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param int ntfyPriorityDown: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str, optional ntfyIcon: Notification option for ``type`` :attr:`~.NotificationType.NTFY`.
        :param str, optional octopushVersion: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str octopushAPIKey: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str octopushLogin: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str octopushPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str, optional octopushSMSType: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str, optional octopushSenderName: Notification option for ``type`` :attr:`~.NotificationType.OCTOPUSH`.
        :param str httpAddr: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`.
        :param str accessToken: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`.
        :param str, optional msgType: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`.
        :param str recieverId: Notification option for ``type`` :attr:`~.NotificationType.ONEBOT`.
        :param str accessToken: Notification option for ``type`` :attr:`~.NotificationType.ONECHAT`.
        :param str recieverId: Notification option for ``type`` :attr:`~.NotificationType.ONECHAT`.
        :param str botId: Notification option for ``type`` :attr:`~.NotificationType.ONECHAT`.
        :param str onesenderReceiver: Notification option for ``type`` :attr:`~.NotificationType.ONESENDER`.
        :param str onesenderTypeReceiver: Notification option for ``type`` :attr:`~.NotificationType.ONESENDER`.
        :param str onesenderToken: Notification option for ``type`` :attr:`~.NotificationType.ONESENDER`.
        :param str onesenderURL: Notification option for ``type`` :attr:`~.NotificationType.ONESENDER`.
        :param str, optional ooredooServerUrl: Notification option for ``type`` :attr:`~.NotificationType.OOREDOO`.
        :param str ooredooToNumber: Notification option for ``type`` :attr:`~.NotificationType.OOREDOO`.
        :param str ooredooBearerToken: Notification option for ``type`` :attr:`~.NotificationType.OOREDOO`.
        :param str ooredooUsername: Notification option for ``type`` :attr:`~.NotificationType.OOREDOO`.
        :param str ooredooAccessKey: Notification option for ``type`` :attr:`~.NotificationType.OOREDOO`.
        :param str, optional openwaCustomMessage: Notification option for ``type`` :attr:`~.NotificationType.OPENWA`.
        :param bool, optional openwaUseCustomMessage: Notification option for ``type`` :attr:`~.NotificationType.OPENWA`.
        :param str openwaApiKey: Notification option for ``type`` :attr:`~.NotificationType.OPENWA`.
        :param str openwaChatId: Notification option for ``type`` :attr:`~.NotificationType.OPENWA`.
        :param str openwaApiUrl: Notification option for ``type`` :attr:`~.NotificationType.OPENWA`.
        :param str openwaSession: Notification option for ``type`` :attr:`~.NotificationType.OPENWA`.
        :param int, optional opsgeniePriority: Notification option for ``type`` :attr:`~.NotificationType.OPSGENIE`. Priority. Available values are numbers between ``1`` and ``5``.
        :param str opsgenieRegion: Notification option for ``type`` :attr:`~.NotificationType.OPSGENIE`. Region. Available values are:

            - ``us``: US (Default)
            - ``eu``: EU
        :param str opsgenieApiKey: Notification option for ``type`` :attr:`~.NotificationType.OPSGENIE`. API Key.
        :param str, optional pagerdutyAutoResolve: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`.
        :param str, optional pagerdutyIntegrationUrl: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`.
        :param str, optional pagerdutyPriority: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`.
        :param str pagerdutyIntegrationKey: Notification option for ``type`` :attr:`~.NotificationType.PAGERDUTY`.
        :param str, optional pagertreeAutoResolve: Notification option for ``type`` :attr:`~.NotificationType.PAGERTREE`.

            Available values are:

            - ``0``: Do Nothing
            - ``resolve``: Auto Resolve
        :param str, optional pagertreeIntegrationUrl: Notification option for ``type`` :attr:`~.NotificationType.PAGERTREE`.
        :param str, optional pagertreeUrgency: Notification option for ``type`` :attr:`~.NotificationType.PAGERTREE`.

            Available values are:

            - ``silent``: Silent
            - ``low``: Low
            - ``medium``: Medium
            - ``high``: High
            - ``critical``: Critical
        :param str pingletPublishUrl: Notification option for ``type`` :attr:`~.NotificationType.PINGLET`.
        :param str pingletApiKey: Notification option for ``type`` :attr:`~.NotificationType.PINGLET`.
        :param str plivoAuthID: Notification option for ``type`` :attr:`~.NotificationType.PLIVO`.
        :param str plivoAuthToken: Notification option for ``type`` :attr:`~.NotificationType.PLIVO`.
        :param str, optional plivoMessageType: Notification option for ``type`` :attr:`~.NotificationType.PLIVO`.
        :param str, optional plivoAnswerUrl: Notification option for ``type`` :attr:`~.NotificationType.PLIVO`.
        :param str plivoFromNumber: Notification option for ``type`` :attr:`~.NotificationType.PLIVO`.
        :param str plivoToNumber: Notification option for ``type`` :attr:`~.NotificationType.PLIVO`.
        :param bool, optional promosmsAllowLongSMS: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`. Allow long SMS.
        :param str promosmsLogin: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`.
        :param str promosmsPassword: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`.
        :param str promosmsPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`. Phone number (for Polish recipient You can skip area codes).
        :param str, optional promosmsSMSType: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`.

            Available values are:

            - ``0``: SMS FLASH - Message will automatically show on recipient device. Limited only to Polish recipients.
            - ``1``: SMS ECO - cheap but slow and often overloaded. Limited only to Polish recipients.
            - ``3``: SMS FULL - Premium tier of SMS, You can use your Sender Name (You need to register name first). Reliable for alerts.
            - ``4``: SMS SPEED - Highest priority in system. Very quick and reliable but costly (about twice of SMS FULL price).
        :param str, optional promosmsSenderName: Notification option for ``type`` :attr:`~.NotificationType.PROMOSMS`.
        :param str webhookURL: Notification option for ``type`` :attr:`~.NotificationType.PUMBLE`.
        :param str pushbulletAccessToken: Notification option for ``type`` :attr:`~.NotificationType.PUSHBULLET`.
        :param str, optional pushdeerServer: Notification option for ``type`` :attr:`~.NotificationType.PUSHDEER`.
        :param str pushdeerKey: Notification option for ``type`` :attr:`~.NotificationType.PUSHDEER`.
        :param str pushoveruserkey: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str pushoverapptoken: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str, optional pushoversounds: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str, optional pushoverpriority: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str, optional pushovertitle: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str, optional pushoverdevice: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param int, optional pushoverttl: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`. Message TTL (Seconds).
        :param str, optional pushoversounds_up: Notification option for ``type`` :attr:`~.NotificationType.PUSHOVER`.
        :param str pushPlusSendKey: Notification option for ``type`` :attr:`~.NotificationType.PUSHPLUS`.
        :param str pushyAPIKey: Notification option for ``type`` :attr:`~.NotificationType.PUSHY`.
        :param str pushyToken: Notification option for ``type`` :attr:`~.NotificationType.PUSHY`.
        :param str resendApiKey: Notification option for ``type`` :attr:`~.NotificationType.RESEND`.
        :param str resendFromEmail: Notification option for ``type`` :attr:`~.NotificationType.RESEND`.
        :param str, optional resendFromName: Notification option for ``type`` :attr:`~.NotificationType.RESEND`.
        :param str resendToEmail: Notification option for ``type`` :attr:`~.NotificationType.RESEND`.
        :param str, optional resendSubject: Notification option for ``type`` :attr:`~.NotificationType.RESEND`.
        :param str, optional rocketchannel: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`.
        :param str, optional rocketusername: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`.
        :param str, optional rocketiconemo: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`.
        :param str rocketwebhookURL: Notification option for ``type`` :attr:`~.NotificationType.ROCKET_CHAT`.
        :param str sendgridApiKey: Notification option for ``type`` :attr:`~.NotificationType.SENDGRID`.
        :param str sendgridToEmail: Notification option for ``type`` :attr:`~.NotificationType.SENDGRID`.
        :param str, optional sendgridCcEmail: Notification option for ``type`` :attr:`~.NotificationType.SENDGRID`.
        :param str, optional sendgridBccEmail: Notification option for ``type`` :attr:`~.NotificationType.SENDGRID`.
        :param str sendgridFromEmail: Notification option for ``type`` :attr:`~.NotificationType.SENDGRID`.
        :param str, optional sendgridSubject: Notification option for ``type`` :attr:`~.NotificationType.SENDGRID`.
        :param str serverChanSendKey: Notification option for ``type`` :attr:`~.NotificationType.SERVERCHAN`.
        :param str serwersmsUsername: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`.
        :param str serwersmsPassword: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`.
        :param str, optional serwersmsSenderName: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`.
        :param str, optional serwersmsRecipientType: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`.
        :param str, optional serwersmsGroupId: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`.
        :param str, optional serwersmsPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.SERWERSMS`.
        :param int sevenioReceiver: Notification option for ``type`` :attr:`~.NotificationType.SEVENIO`.
        :param str, optional sevenioSender: Notification option for ``type`` :attr:`~.NotificationType.SEVENIO`.
        :param str sevenioApiKey: Notification option for ``type`` :attr:`~.NotificationType.SEVENIO`.
        :param bool, optional signalUseTemplate: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`.
        :param str, optional signalTemplate: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`.
        :param str signalNumber: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`.
        :param str signalRecipients: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`.
        :param str signalURL: Notification option for ``type`` :attr:`~.NotificationType.SIGNAL`.
        :param str signalgridClientKey: Notification option for ``type`` :attr:`~.NotificationType.SIGNALGRID`.
        :param str signalgridChannel: Notification option for ``type`` :attr:`~.NotificationType.SIGNALGRID`.
        :param str webhookURL: Notification option for ``type`` :attr:`~.NotificationType.SIGNL4`.
        :param bool, optional slackchannelnotify: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str, optional slackchannel: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str, optional slackusername: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str, optional slackiconemo: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str slackwebhookURL: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param bool, optional slackUseTemplate: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str, optional slackTemplate: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param bool, optional slackIncludeGroupName: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param bool, optional slackrichmessage: Notification option for ``type`` :attr:`~.NotificationType.SLACK`.
        :param str smsgatewayUrl: Notification option for ``type`` :attr:`~.NotificationType.SMSGATEWAY`.
        :param str smsgatewayTo: Notification option for ``type`` :attr:`~.NotificationType.SMSGATEWAY`.
        :param str smsgatewayApiKey: Notification option for ``type`` :attr:`~.NotificationType.SMSGATEWAY`.
        :param str smsplanetApiToken: Notification option for ``type`` :attr:`~.NotificationType.SMSPLANET`.
        :param str, optional smsplanetSenderName: Notification option for ``type`` :attr:`~.NotificationType.SMSPLANET`.
        :param str smsplanetPhoneNumbers: Notification option for ``type`` :attr:`~.NotificationType.SMSPLANET`.
        :param str, optional smscTranslit: Notification option for ``type`` :attr:`~.NotificationType.SMSC`.
        :param str smscLogin: Notification option for ``type`` :attr:`~.NotificationType.SMSC`.
        :param str smscPassword: Notification option for ``type`` :attr:`~.NotificationType.SMSC`.
        :param str smscToNumber: Notification option for ``type`` :attr:`~.NotificationType.SMSC`.
        :param str, optional smscSenderName: Notification option for ``type`` :attr:`~.NotificationType.SMSC`.
        :param str, optional smseagleApiType: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`.
        :param str, optional smseagleRecipientType: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. Recipient type.

            Available values are:

            - ``smseagle-to``: Phone number(s)
            - ``smseagle-group``: Phonebook group name(s)
            - ``smseagle-contact``: Phonebook contact name(s)
        :param str, optional smseagleMsgType: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`.
        :param int, optional smseagleDuration: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`.
        :param int, optional smseagleTtsModel: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`.
        :param str smseagleUrl: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. Your SMSEagle device URL.
        :param str smseagleToken: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. API Access token.
        :param str, optional smseagleRecipient: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. Recipient(s) (multiple must be separated with comma).
        :param bool, optional smseagleEncoding: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. True to send messages in unicode.
        :param int, optional smseaglePriority: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`. Message priority (0-9, default = 0).
        :param str, optional smseagleRecipientContact: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`.
        :param str, optional smseagleRecipientGroup: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`.
        :param str, optional smseagleRecipientTo: Notification option for ``type`` :attr:`~.NotificationType.SMSEAGLE`.
        :param str smsirApiKey: Notification option for ``type`` :attr:`~.NotificationType.SMSIR`.
        :param str smsirNumber: Notification option for ``type`` :attr:`~.NotificationType.SMSIR`.
        :param str smsirTemplate: Notification option for ``type`` :attr:`~.NotificationType.SMSIR`.
        :param str, optional smsmanagerApiKey: Notification option for ``type`` :attr:`~.NotificationType.SMSMANAGER`.
        :param str, optional numbers: Notification option for ``type`` :attr:`~.NotificationType.SMSMANAGER`.
        :param str, optional messageType: Notification option for ``type`` :attr:`~.NotificationType.SMSMANAGER`.
        :param str smspartnerApikey: Notification option for ``type`` :attr:`~.NotificationType.SMSPARTNER`.
        :param str smspartnerSenderName: Notification option for ``type`` :attr:`~.NotificationType.SMSPARTNER`.
        :param str smspartnerPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.SMSPARTNER`.
        :param str smtpHost: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param int smtpPort: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpSecure: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param bool, optional smtpIgnoreSTARTTLS: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param bool, optional smtpIgnoreTLSError: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpDkimDomain: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpDkimKeySelector: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpDkimPrivateKey: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpDkimHashAlgo: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpDkimheaderFieldNames: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpDkimskipFields: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpUsername: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpPassword: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpAdditionalHeaders: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional customSubject: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional customBody: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param bool, optional htmlBody: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str smtpFrom: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpCC: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpBCC: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional smtpTo: Notification option for ``type`` :attr:`~.NotificationType.SMTP`.
        :param str, optional splunkAutoResolve: Notification option for ``type`` :attr:`~.NotificationType.SPLUNK`. Auto resolve or acknowledged.

            Available values are:

            - ``0``: do nothing
            - ``ACKNOWLEDGEMENT``: auto acknowledged
            - ``RECOVERY``: auto resolve
        :param str, optional splunkSeverity: Notification option for ``type`` :attr:`~.NotificationType.SPLUNK`. Severity.

            Available values are:

            - ``INFO``
            - ``WARNING``
            - ``CRITICAL``
        :param str splunkRestURL: Notification option for ``type`` :attr:`~.NotificationType.SPLUNK`. Splunk Rest URL.
        :param str templateKey: Notification option for ``type`` :attr:`~.NotificationType.SPUGPUSH`.
        :param str squadcastWebhookURL: Notification option for ``type`` :attr:`~.NotificationType.SQUADCAST`.
        :param str stackfieldwebhookURL: Notification option for ``type`` :attr:`~.NotificationType.STACKFIELD`.
        :param str webhookUrl: Notification option for ``type`` :attr:`~.NotificationType.TEAMS`.
        :param bool, optional teamsEnableTags: Notification option for ``type`` :attr:`~.NotificationType.TEAMS`.
        :param str, optional pushTitle: Notification option for ``type`` :attr:`~.NotificationType.PUSHBYTECHULUS`.
        :param bool, optional pushTimeSensitive: Notification option for ``type`` :attr:`~.NotificationType.PUSHBYTECHULUS`.
        :param str, optional pushChannel: Notification option for ``type`` :attr:`~.NotificationType.PUSHBYTECHULUS`.
        :param str, optional pushSound: Notification option for ``type`` :attr:`~.NotificationType.PUSHBYTECHULUS`.
        :param str pushAPIKey: Notification option for ``type`` :attr:`~.NotificationType.PUSHBYTECHULUS`.
        :param str, optional telegramServerUrl: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param str telegramChatID: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param bool, optional telegramSendSilently: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param bool, optional telegramProtectContent: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param str, optional telegramMessageThreadID: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param bool, optional telegramUseTemplate: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param str, optional telegramTemplateParseMode: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param str, optional telegramTemplate: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param str telegramBotToken: Notification option for ``type`` :attr:`~.NotificationType.TELEGRAM`.
        :param str telnyxPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.TELNYX`.
        :param str telnyxToNumber: Notification option for ``type`` :attr:`~.NotificationType.TELNYX`.
        :param str, optional telnyxMessagingProfileId: Notification option for ``type`` :attr:`~.NotificationType.TELNYX`.
        :param str telnyxApiKey: Notification option for ``type`` :attr:`~.NotificationType.TELNYX`.
        :param str teltonikaUrl: Notification option for ``type`` :attr:`~.NotificationType.TELTONIKA`.
        :param bool, optional teltonikaUnsafeTls: Notification option for ``type`` :attr:`~.NotificationType.TELTONIKA`.
        :param str teltonikaUsername: Notification option for ``type`` :attr:`~.NotificationType.TELTONIKA`.
        :param str teltonikaPassword: Notification option for ``type`` :attr:`~.NotificationType.TELTONIKA`.
        :param str teltonikaModem: Notification option for ``type`` :attr:`~.NotificationType.TELTONIKA`.
        :param str teltonikaPhoneNumber: Notification option for ``type`` :attr:`~.NotificationType.TELTONIKA`.
        :param str threemaSenderIdentity: Notification option for ``type`` :attr:`~.NotificationType.THREEMA`.
        :param str threemaSecret: Notification option for ``type`` :attr:`~.NotificationType.THREEMA`.
        :param str threemaRecipientType: Notification option for ``type`` :attr:`~.NotificationType.THREEMA`.
        :param str, optional threemaRecipient: Notification option for ``type`` :attr:`~.NotificationType.THREEMA`.
        :param str turbosmtpConsumerKey: Notification option for ``type`` :attr:`~.NotificationType.TURBOSMTP`.
        :param str turbosmtpConsumerSecret: Notification option for ``type`` :attr:`~.NotificationType.TURBOSMTP`.
        :param str turbosmtpRegion: Notification option for ``type`` :attr:`~.NotificationType.TURBOSMTP`.
        :param str turbosmtpFromEmail: Notification option for ``type`` :attr:`~.NotificationType.TURBOSMTP`.
        :param str turbosmtpToEmail: Notification option for ``type`` :attr:`~.NotificationType.TURBOSMTP`.
        :param str, optional turbosmtpSubject: Notification option for ``type`` :attr:`~.NotificationType.TURBOSMTP`.
        :param str, optional turbosmtpCcEmail: Notification option for ``type`` :attr:`~.NotificationType.TURBOSMTP`.
        :param str, optional turbosmtpBccEmail: Notification option for ``type`` :attr:`~.NotificationType.TURBOSMTP`.
        :param str, optional twilioApiKey: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`.
        :param str twilioAccountSID: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`. Account SID.
        :param str twilioAuthToken: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`. Auth Token.
        :param str twilioToNumber: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`. To Number.
        :param str twilioFromNumber: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`. From Number.
        :param str, optional twilioMessagingServiceSID: Notification option for ``type`` :attr:`~.NotificationType.TWILIO`.
        :param str vkAccessToken: Notification option for ``type`` :attr:`~.NotificationType.VK`.
        :param str vkApiVersion: Notification option for ``type`` :attr:`~.NotificationType.VK`.
        :param str vkPeerId: Notification option for ``type`` :attr:`~.NotificationType.VK`.
        :param bool, optional vkDontParseLinks: Notification option for ``type`` :attr:`~.NotificationType.VK`.
        :param str vkteamsBaseUrl: Notification option for ``type`` :attr:`~.NotificationType.VKTEAMS`.
        :param str vkteamsBotToken: Notification option for ``type`` :attr:`~.NotificationType.VKTEAMS`.
        :param str vkteamsChatId: Notification option for ``type`` :attr:`~.NotificationType.VKTEAMS`.
        :param bool, optional vkteamsUseTemplate: Notification option for ``type`` :attr:`~.NotificationType.VKTEAMS`.
        :param str, optional vkteamsTemplate: Notification option for ``type`` :attr:`~.NotificationType.VKTEAMS`.
        :param str, optional vkteamsTemplateFormat: Notification option for ``type`` :attr:`~.NotificationType.VKTEAMS`.
        :param str, optional wahaApiKey: Notification option for ``type`` :attr:`~.NotificationType.WAHA`.
        :param str wahaSession: Notification option for ``type`` :attr:`~.NotificationType.WAHA`.
        :param str wahaChatId: Notification option for ``type`` :attr:`~.NotificationType.WAHA`.
        :param str wahaApiUrl: Notification option for ``type`` :attr:`~.NotificationType.WAHA`.
        :param str, optional httpMethod: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`.
        :param str, optional webhookContentType: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`.
        :param str, optional webhookCustomBody: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`.
        :param str, optional webhookAdditionalHeaders: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`.
        :param str webhookURL: Notification option for ``type`` :attr:`~.NotificationType.WEBHOOK`.
        :param str weComBotKey: Notification option for ``type`` :attr:`~.NotificationType.WECOM`.
        :param str, optional weComMentionedMobileList: Notification option for ``type`` :attr:`~.NotificationType.WECOM`.
        :param str whapiAuthToken: Notification option for ``type`` :attr:`~.NotificationType.WHAPI`.
        :param str whapiRecipient: Notification option for ``type`` :attr:`~.NotificationType.WHAPI`.
        :param str, optional whapiApiUrl: Notification option for ``type`` :attr:`~.NotificationType.WHAPI`.
        :param str wpushAPIkey: Notification option for ``type`` :attr:`~.NotificationType.WPUSH`.
        :param str wpushChannel: Notification option for ``type`` :attr:`~.NotificationType.WPUSH`.
        :param str wxpusherSPT: Notification option for ``type`` :attr:`~.NotificationType.WXPUSHER`.
        :param str yzjWebHookUrl: Notification option for ``type`` :attr:`~.NotificationType.YZJ`.
        :param str yzjToken: Notification option for ``type`` :attr:`~.NotificationType.YZJ`.
        :param str webhookUrl: Notification option for ``type`` :attr:`~.NotificationType.ZOHOCLIQ`.
    """


def proxy_docstring(mode) -> str:
    return f"""
        :param ProxyProtocol{", optional" if mode == "edit" else ""} protocol: Proxy Protocol
        :param str{", optional" if mode == "edit" else ""} host: Proxy Server
        :param str{", optional" if mode == "edit" else ""} port: Port
        :param bool, optional auth: Proxy server has authentication, defaults to False
        :param str, optional username: User, defaults to None
        :param str, optional password: Password, defaults to None
        :param bool, optional active: Enabled. This proxy will not effect on monitor requests until it is activated. You can control temporarily disable the proxy from all monitors by activation status., defaults to True
        :param bool, optional default: Set As Default. This proxy will be enabled by default for new monitors. You can still disable the proxy separately for each monitor., , defaults to False
        :param bool, optional applyExisting: Apply on all existing monitors, defaults to False
    """


def docker_host_docstring(mode) -> str:
    return f"""
        :param str{", optional" if mode == "edit" else ""} name: Friendly Name
        :param DockerType{", optional" if mode == "edit" else ""} dockerType: Connection Type
        :param str, optional dockerDaemon: Docker Daemon, defaults to None
    """


def maintenance_docstring(mode) -> str:
    return f"""
        :param str{", optional" if mode == "edit" else ""} title: Title
        :param MaintenanceStrategy{", optional" if mode == "edit" else ""} strategy: Strategy
        :param bool, optional active: True if maintenance is active, defaults to ``True``
        :param str, optional description: Description, defaults to ``""``
        :param list, optional dateRange: DateTime Range, defaults to ``["<current date>"]``
        :param int, optional intervalDay: Interval (Run once every day), defaults to ``1``
        :param list, optional weekdays: List that contains the days of the week on which the maintenance is enabled (Sun = ``0``, Mon = ``1``, ..., Sat = ``6``). Required for ``strategy`` :attr:`~.MaintenanceStrategy.RECURRING_WEEKDAY`., defaults to ``[]``.
        :param list, optional daysOfMonth: List that contains the days of the month on which the maintenance is enabled (Day 1 = ``1``, Day 2 = ``2``, ..., Day 31 = ``31``) and the last day of the month (``"lastDay1"``). Required for ``strategy`` :attr:`~.MaintenanceStrategy.RECURRING_DAY_OF_MONTH`., defaults to ``[]``.
        :param list, optional timeRange: Maintenance Time Window of a Day, defaults to ``[{{"hours": 2, "minutes": 0}}, {{"hours": 3, "minutes": 0}}]``.
        :param str, optional cron: Cron Schedule. Required for ``strategy`` :attr:`~.MaintenanceStrategy.CRON`., defaults to ``"30 3 * * *"``
        :param int, optional durationMinutes: Duration (Minutes). Required for ``strategy`` :attr:`~.MaintenanceStrategy.CRON`., defaults to ``60``
        :param str, optional timezone: Timezone, defaults to ``None`` (Server Timezone)
    """


def tag_docstring(mode) -> str:
    return f"""
        :param str{", optional" if mode == "edit" else ""} name: Tag name
        :param str{", optional" if mode == "edit" else ""} color: Tag color
    """
