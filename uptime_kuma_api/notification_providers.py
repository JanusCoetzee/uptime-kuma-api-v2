from enum import Enum


class NotificationType(str, Enum):
    """Enumerate notification types."""

    WHATSAPP360MESSENGER = "Whatsapp360messenger"
    """WhatsApp (360messenger)"""

    ELKS = "Elks"
    """46elks"""

    HALOPSA = "HaloPSA"
    """Halo PSA"""

    WEBPUSH = "Webpush"
    """Webpush"""

    ALERTA = "alerta"
    """Alerta"""

    ALERTNOW = "AlertNow"
    """AlertNow"""

    ALIYUNSMS = "AliyunSMS"
    """AliyunSMS"""

    AMOOTSMS = "amootsms"
    """Amoot SMS"""

    APPRISE = "apprise"
    """Apprise (Support 50+ Notification services)"""

    BALE = "bale"
    """Bale"""

    BARK = "Bark"
    """Bark"""

    BEARSMS = "bearsms"
    """BearSMS (Israel)"""

    BITRIX24 = "Bitrix24"
    """Bitrix24"""

    BREVO = "Brevo"
    """Brevo"""

    CALLMEBOT = "CallMeBot"
    """CallMeBot (WhatsApp, Telegram Call, Facebook Messenger)"""

    CELLSYNT = "Cellsynt"
    """Cellsynt"""

    CLICKSENDSMS = "clicksendsms"
    """ClickSend SMS"""

    CLICKUP = "ClickUp"
    """ClickUp"""

    DINGDING = "DingDing"
    """DingDing"""

    DISCORD = "discord"
    """Discord"""

    EGOSMS = "egosms"
    """EgoSMS (Uganda)"""

    EVOLUTION = "evolution"
    """WhatsApp (Evolution)"""

    FEISHU = "Feishu"
    """Feishu"""

    FLASHDUTY = "FlashDuty"
    """FlashDuty"""

    FLOWTRIQ = "Flowtriq"
    """Flowtriq"""

    FLUXER = "fluxer"
    """Fluxer"""

    FREEMOBILE = "FreeMobile"
    """FreeMobile (mobile.free.fr)"""

    GOALERT = "GoAlert"
    """GoAlert"""

    GOOGLECHAT = "GoogleChat"
    """Google Chat (Google Workspace)"""

    GOOGLESHEETS = "GoogleSheets"
    """Google Sheets"""

    GORUSH = "gorush"
    """Gorush"""

    GOTIFY = "gotify"
    """Gotify"""

    GRAFANAONCALL = "GrafanaOncall"
    """Grafana Oncall"""

    GTXMESSAGING = "gtxmessaging"
    """GtxMessaging"""

    HEIIONCALL = "HeiiOnCall"
    """Heii On-Call"""

    HOMEASSISTANT = "HomeAssistant"
    """Home Assistant"""

    JIRASERVICEMANAGEMENT = "JiraServiceManagement"
    """Jira Service Management"""

    KEEP = "Keep"
    """Keep"""

    KOOK = "Kook"
    """Kook"""

    LINE = "line"
    """LINE Messenger"""

    LUNASEA = "lunasea"
    """LunaSea"""

    MATRIX = "matrix"
    """Matrix"""

    MATTERMOST = "mattermost"
    """Mattermost"""

    MAX = "max"
    """MAX messenger"""

    MILKY = "Milky"
    """Milky(QQ)"""

    NEXTCLOUDTALK = "nextcloudtalk"
    """Nextcloud Talk"""

    NOSTR = "nostr"
    """Nostr"""

    NOTIFERY = "notifery"
    """Notifery"""

    NOTIFYAPP = "notifyapp"
    """Notify!"""

    NTFY = "ntfy"
    """Ntfy"""

    OCTOPUSH = "octopush"
    """Octopush"""

    ONEBOT = "OneBot"
    """OneBot"""

    ONECHAT = "OneChat"
    """OneChat"""

    ONESENDER = "Onesender"
    """Onesender"""

    OOREDOO = "Ooredoo"
    """Ooredoo (Maldives)"""

    OPENWA = "openwa"
    """WhatsApp (OpenWA)"""

    OPSGENIE = "Opsgenie"
    """Opsgenie"""

    PAGERDUTY = "PagerDuty"
    """PagerDuty"""

    PAGERTREE = "PagerTree"
    """PagerTree"""

    PINGLET = "pinglet"
    """Pinglet"""

    PLIVO = "plivo"
    """Plivo"""

    PROMOSMS = "promosms"
    """PromoSMS"""

    PUMBLE = "pumble"
    """Pumble"""

    PUSHBULLET = "pushbullet"
    """Pushbullet"""

    PUSHDEER = "PushDeer"
    """PushDeer"""

    PUSHOVER = "pushover"
    """Pushover"""

    PUSHPLUS = "PushPlus"
    """PushPlus (推送加)"""

    PUSHY = "pushy"
    """Pushy"""

    RESEND = "Resend"
    """Resend"""

    ROCKET_CHAT = "rocket.chat"
    """Rocket.Chat"""

    SENDGRID = "SendGrid"
    """SendGrid"""

    SERVERCHAN = "ServerChan"
    """ServerChan"""

    SERWERSMS = "serwersms"
    """SerwerSMS.pl"""

    SEVENIO = "SevenIO"
    """SevenIO"""

    SIGNAL = "signal"
    """Signal"""

    SIGNALGRID = "signalgrid"
    """Signalgrid"""

    SIGNL4 = "SIGNL4"
    """SIGNL4"""

    SLACK = "slack"
    """Slack"""

    SMSGATEWAY = "SMSGateway"
    """SMS Gateway"""

    SMSPLANET = "SMSPlanet"
    """SMSPlanet.pl"""

    SMSC = "smsc"
    """SMSC"""

    SMSEAGLE = "SMSEagle"
    """SMSEagle"""

    SMSIR = "smsir"
    """SMS.IR"""

    SMSMANAGER = "SMSManager"
    """SmsManager (smsmanager.cz)"""

    SMSPARTNER = "SMSPartner"
    """SMS Partner"""

    SMTP = "smtp"
    """Email (SMTP)"""

    SPLUNK = "Splunk"
    """Splunk"""

    SPUGPUSH = "SpugPush"
    """SpugPush（Spug推送助手）"""

    SQUADCAST = "squadcast"
    """SquadCast"""

    STACKFIELD = "stackfield"
    """Stackfield"""

    TEAMS = "teams"
    """Microsoft Teams"""

    PUSHBYTECHULUS = "PushByTechulus"
    """Push by Techulus"""

    TELEGRAM = "telegram"
    """Telegram"""

    TELNYX = "telnyx"
    """Telnyx"""

    TELTONIKA = "Teltonika"
    """Teltonika SMS Gateway"""

    THREEMA = "threema"
    """Threema"""

    TURBOSMTP = "TurboSMTP"
    """TurboSMTP"""

    TWILIO = "twilio"
    """Twilio"""

    VK = "VK"
    """VK"""

    VKTEAMS = "VKTeams"
    """VKTeams"""

    WAHA = "waha"
    """WhatsApp (WAHA)"""

    WEBHOOK = "webhook"
    """Webhook"""

    WECOM = "WeCom"
    """WeCom"""

    WHAPI = "whapi"
    """WhatsApp (Whapi)"""

    WPUSH = "WPush"
    """WPush(wpush.cn)"""

    WXPUSHER = "WxPusher"
    """WxPusher SPT Push (WxPusher极简推送)"""

    YZJ = "YZJ"
    """YZJ (云之家自定义机器人)"""

    ZOHOCLIQ = "ZohoCliq"
    """ZohoCliq"""


notification_provider_options = {
    NotificationType.WHATSAPP360MESSENGER: dict(
        Whatsapp360messengerAuthToken=dict(type="str", required=True),
        Whatsapp360messengerUseTemplate=dict(type="bool", required=False),
        Whatsapp360messengerTemplate=dict(type="str", required=False),
        Whatsapp360messengerRecipient=dict(type="str", required=False),
        Whatsapp360messengerGroupIds=dict(type="str", required=False),
    ),
    NotificationType.ELKS: dict(
        elksFromNumber=dict(type="str", required=True),
        elksToNumber=dict(type="str", required=True),
        elksUsername=dict(type="str", required=True),
        elksAuthToken=dict(type="str", required=True),
    ),
    NotificationType.HALOPSA: dict(
        haloUsername=dict(type="str", required=False),
        haloPassword=dict(type="str", required=False),
        halowebhookurl=dict(type="str", required=True),
    ),
    NotificationType.WEBPUSH: dict(
    ),
    NotificationType.ALERTA: dict(
        alertaApiKey=dict(type="str", required=True),
        alertaEnvironment=dict(type="str", required=True),
        alertaApiEndpoint=dict(type="str", required=True),
        alertaAlertState=dict(type="str", required=True),
        alertaRecoverState=dict(type="str", required=True),
    ),
    NotificationType.ALERTNOW: dict(
        alertNowWebhookURL=dict(type="str", required=True),
    ),
    NotificationType.ALIYUNSMS: dict(
        optionalParameters=dict(type="bool", required=False),
        phonenumber=dict(type="str", required=True),
        templateCode=dict(type="str", required=True),
        signName=dict(type="str", required=True),
        accessKeyId=dict(type="str", required=True),
        secretAccessKey=dict(type="str", required=True),
    ),
    NotificationType.AMOOTSMS: dict(
        amootMobiles=dict(type="str", required=True),
        amootApiToken=dict(type="str", required=True),
        amootUsePattern=dict(type="bool", required=False),
        amootPatternCodeId=dict(type="int", required=False),
        amootUseOwnLine=dict(type="bool", required=False),
        amootLineNumber=dict(type="str", required=False),
    ),
    NotificationType.APPRISE: dict(
        appriseURL=dict(type="str", required=True),
        title=dict(type="str", required=False),
    ),
    NotificationType.BALE: dict(
        baleBotToken=dict(type="str", required=True),
        baleChatID=dict(type="str", required=True),
    ),
    NotificationType.BARK: dict(
        barkEndpoint=dict(type="str", required=True),
        barkGroup=dict(type="str", required=True),
        barkSound=dict(type="str", required=True),
        apiVersion=dict(type="str", required=True),
    ),
    NotificationType.BEARSMS: dict(
        bearsmsUsername=dict(type="str", required=True),
        bearsmsHashKey=dict(type="str", required=True),
        bearsmsPhoneNumber=dict(type="str", required=True),
        bearsmsSenderId=dict(type="str", required=False),
    ),
    NotificationType.BITRIX24: dict(
        bitrix24UserID=dict(type="str", required=True),
        bitrix24WebhookURL=dict(type="str", required=True),
    ),
    NotificationType.BREVO: dict(
        brevoApiKey=dict(type="str", required=True),
        brevoToEmail=dict(type="str", required=True),
        brevoFromEmail=dict(type="str", required=True),
        brevoFromName=dict(type="str", required=False),
        brevoSubject=dict(type="str", required=False),
        brevoCcEmail=dict(type="str", required=False),
        brevoBccEmail=dict(type="str", required=False),
    ),
    NotificationType.CALLMEBOT: dict(
        callMeBotEndpoint=dict(type="str", required=True),
    ),
    NotificationType.CELLSYNT: dict(
        cellsyntLogin=dict(type="str", required=True),
        cellsyntPassword=dict(type="str", required=True),
        cellsyntDestination=dict(type="str", required=True),
        cellsyntOriginatortype=dict(type="str", required=True),
        cellsyntOriginator=dict(type="int", required=False),
        cellsyntAllowLongSMS=dict(type="bool", required=False),
    ),
    NotificationType.CLICKSENDSMS: dict(
        clicksendsmsLogin=dict(type="str", required=True),
        clicksendsmsPassword=dict(type="str", required=True),
        clicksendsmsToNumber=dict(type="str", required=True),
        clicksendsmsSenderName=dict(type="str", required=False),
    ),
    NotificationType.CLICKUP: dict(
        clickupToken=dict(type="str", required=True),
        clickupDisableUrl=dict(type="bool", required=False),
        clickupWorkspaceId=dict(type="str", required=True),
        clickupChannelId=dict(type="str", required=True),
    ),
    NotificationType.DINGDING: dict(
        mentioning=dict(type="str", required=True),
        mobileList=dict(type="str", required=False),
        userList=dict(type="str", required=False),
        webHookUrl=dict(type="str", required=True),
        secretKey=dict(type="str", required=True),
    ),
    NotificationType.DISCORD: dict(
        discordUsername=dict(type="str", required=False),
        discordWebhookUrl=dict(type="str", required=True),
        discordChannelType=dict(type="str", required=False),
        threadId=dict(type="str", required=False),
        discordMessageFormat=dict(type="str", required=False),
        discordMessageTemplate=dict(type="str", required=False),
        postName=dict(type="str", required=False),
        discordSuppressNotifications=dict(type="bool", required=False),
        disableUrl=dict(type="bool", required=False),
        discordPrefixMessage=dict(type="str", required=False),
    ),
    NotificationType.EGOSMS: dict(
        egosmsPhoneNumber=dict(type="str", required=True),
        egosmsUsername=dict(type="str", required=True),
        egosmsPassword=dict(type="str", required=True),
        egosmsSender=dict(type="str", required=False),
    ),
    NotificationType.EVOLUTION: dict(
        evolutionAuthToken=dict(type="str", required=True),
        evolutionCustomMessage=dict(type="str", required=False),
        evolutionUseCustomMessage=dict(type="bool", required=False),
        evolutionRecipient=dict(type="str", required=True),
        evolutionApiUrl=dict(type="str", required=False),
        evolutionInstanceName=dict(type="str", required=True),
    ),
    NotificationType.FEISHU: dict(
        feishuWebHookUrl=dict(type="str", required=True),
    ),
    NotificationType.FLASHDUTY: dict(
        flashdutySeverity=dict(type="str", required=True),
        flashdutyIntegrationKey=dict(type="str", required=False),
    ),
    NotificationType.FLOWTRIQ: dict(
        flowtriqApiKey=dict(type="str", required=False),
        flowtriqWebhookUrl=dict(type="str", required=True),
    ),
    NotificationType.FLUXER: dict(
        fluxerUsername=dict(type="str", required=False),
        fluxerWebhookUrl=dict(type="str", required=True),
        fluxerMessageFormat=dict(type="str", required=False),
        fluxerMessageTemplate=dict(type="str", required=False),
        disableUrl=dict(type="bool", required=False),
        fluxerPrefixMessage=dict(type="str", required=False),
    ),
    NotificationType.FREEMOBILE: dict(
        freemobileUser=dict(type="str", required=True),
        freemobilePass=dict(type="str", required=True),
    ),
    NotificationType.GOALERT: dict(
        goAlertBaseURL=dict(type="str", required=True),
        goAlertToken=dict(type="str", required=True),
    ),
    NotificationType.GOOGLECHAT: dict(
        googleChatMaxRetries=dict(type="int", required=True),
        googleChatUseTemplate=dict(type="bool", required=False),
        googleChatTemplate=dict(type="str", required=False),
        googleChatWebhookURL=dict(type="str", required=True),
    ),
    NotificationType.GOOGLESHEETS: dict(
        googleSheetsWebhookUrl=dict(type="str", required=True),
    ),
    NotificationType.GORUSH: dict(
        gorushDeviceToken=dict(type="str", required=True),
        gorushPlatform=dict(type="str", required=False),
        gorushTitle=dict(type="str", required=False),
        gorushPriority=dict(type="str", required=False),
        gorushRetry=dict(type="int", required=False),
        gorushTopic=dict(type="str", required=False),
        gorushServerURL=dict(type="str", required=True),
    ),
    NotificationType.GOTIFY: dict(
        gotifyserverurl=dict(type="str", required=True),
        gotifyapplicationToken=dict(type="str", required=True),
        gotifyPriority=dict(type="int", required=True),
    ),
    NotificationType.GRAFANAONCALL: dict(
        GrafanaOncallURL=dict(type="str", required=True),
    ),
    NotificationType.GTXMESSAGING: dict(
        gtxMessagingFrom=dict(type="str", required=True),
        gtxMessagingTo=dict(type="str", required=True),
        gtxMessagingApiKey=dict(type="str", required=True),
    ),
    NotificationType.HEIIONCALL: dict(
        heiiOnCallApiKey=dict(type="str", required=True),
        heiiOnCallTriggerId=dict(type="str", required=True),
    ),
    NotificationType.HOMEASSISTANT: dict(
        notificationService=dict(type="str", required=False),
        longLivedAccessToken=dict(type="str", required=True),
        homeAssistantUrl=dict(type="str", required=True),
    ),
    NotificationType.JIRASERVICEMANAGEMENT: dict(
        jsmPriority=dict(type="int", required=False),
        jsmCloudId=dict(type="str", required=True),
        jsmEmail=dict(type="str", required=True),
        jsmApiToken=dict(type="str", required=True),
    ),
    NotificationType.KEEP: dict(
        webhookAPIKey=dict(type="str", required=True),
        webhookURL=dict(type="str", required=True),
    ),
    NotificationType.KOOK: dict(
        kookGuildID=dict(type="str", required=True),
        kookBotToken=dict(type="str", required=True),
    ),
    NotificationType.LINE: dict(
        lineChannelAccessToken=dict(type="str", required=True),
        lineUserID=dict(type="str", required=True),
    ),
    NotificationType.LUNASEA: dict(
        lunaseaTarget=dict(type="str", required=True),
        lunaseaUserID=dict(type="str", required=False),
        lunaseaDevice=dict(type="str", required=False),
    ),
    NotificationType.MATRIX: dict(
        internalRoomId=dict(type="str", required=True),
        accessToken=dict(type="str", required=True),
        matrixUseTemplate=dict(type="bool", required=False),
        matrixTemplate=dict(type="str", required=False),
        homeserverUrl=dict(type="str", required=True),
    ),
    NotificationType.MATTERMOST: dict(
        mattermostusername=dict(type="str", required=False),
        mattermostWebhookUrl=dict(type="str", required=True),
        mattermostchannel=dict(type="str", required=False),
        mattermosticonemo=dict(type="str", required=False),
        mattermosticonurl=dict(type="str", required=False),
    ),
    NotificationType.MAX: dict(
        maxApiUrl=dict(type="str", required=True),
        maxChatID=dict(type="str", required=True),
        maxBotToken=dict(type="str", required=True),
        maxUseTemplate=dict(type="bool", required=False),
        maxTemplate=dict(type="str", required=False),
        maxTemplateFormat=dict(type="str", required=False),
    ),
    NotificationType.MILKY: dict(
        httpAddr=dict(type="str", required=True),
        msgType=dict(type="str", required=False),
        accessToken=dict(type="str", required=True),
        recieverId=dict(type="str", required=True),
    ),
    NotificationType.NEXTCLOUDTALK: dict(
        botSecret=dict(type="str", required=True),
        sendSilentUp=dict(type="bool", required=False),
        sendSilentDown=dict(type="bool", required=False),
        host=dict(type="str", required=False),
        conversationToken=dict(type="str", required=False),
    ),
    NotificationType.NOSTR: dict(
        sender=dict(type="str", required=True),
        recipients=dict(type="str", required=True),
        relays=dict(type="str", required=True),
    ),
    NotificationType.NOTIFERY: dict(
        notiferyTitle=dict(type="str", required=False),
        notiferyGroup=dict(type="str", required=False),
        notiferyApiKey=dict(type="str", required=True),
    ),
    NotificationType.NOTIFYAPP: dict(
        notifyAppIconUrl=dict(type="str", required=False),
        notifyAppDeviceId=dict(type="str", required=True),
        notifyAppToken=dict(type="str", required=True),
    ),
    NotificationType.NTFY: dict(
        ntfyAuthenticationMethod=dict(type="str", required=False),
        ntfyusername=dict(type="str", required=False),
        ntfypassword=dict(type="str", required=False),
        ntfyaccesstoken=dict(type="str", required=False),
        ntfyCall=dict(type="str", required=False),
        ntfytopic=dict(type="str", required=True),
        ntfyUseTemplate=dict(type="bool", required=False),
        ntfyCustomTitle=dict(type="str", required=False),
        ntfyCustomMessage=dict(type="str", required=False),
        ntfyPriority=dict(type="int", required=True),
        ntfyserverurl=dict(type="str", required=True),
        ntfyPriorityDown=dict(type="int", required=True),
        ntfyIcon=dict(type="str", required=False),
    ),
    NotificationType.OCTOPUSH: dict(
        octopushVersion=dict(type="str", required=False),
        octopushAPIKey=dict(type="str", required=True),
        octopushLogin=dict(type="str", required=True),
        octopushPhoneNumber=dict(type="str", required=True),
        octopushSMSType=dict(type="str", required=False),
        octopushSenderName=dict(type="str", required=False),
    ),
    NotificationType.ONEBOT: dict(
        httpAddr=dict(type="str", required=True),
        accessToken=dict(type="str", required=True),
        msgType=dict(type="str", required=False),
        recieverId=dict(type="str", required=True),
    ),
    NotificationType.ONECHAT: dict(
        accessToken=dict(type="str", required=True),
        recieverId=dict(type="str", required=True),
        botId=dict(type="str", required=True),
    ),
    NotificationType.ONESENDER: dict(
        onesenderReceiver=dict(type="str", required=True),
        onesenderTypeReceiver=dict(type="str", required=True),
        onesenderToken=dict(type="str", required=True),
        onesenderURL=dict(type="str", required=True),
    ),
    NotificationType.OOREDOO: dict(
        ooredooServerUrl=dict(type="str", required=False),
        ooredooToNumber=dict(type="str", required=True),
        ooredooBearerToken=dict(type="str", required=True),
        ooredooUsername=dict(type="str", required=True),
        ooredooAccessKey=dict(type="str", required=True),
    ),
    NotificationType.OPENWA: dict(
        openwaCustomMessage=dict(type="str", required=False),
        openwaUseCustomMessage=dict(type="bool", required=False),
        openwaApiKey=dict(type="str", required=True),
        openwaChatId=dict(type="str", required=True),
        openwaApiUrl=dict(type="str", required=True),
        openwaSession=dict(type="str", required=True),
    ),
    NotificationType.OPSGENIE: dict(
        opsgeniePriority=dict(type="int", required=False),
        opsgenieRegion=dict(type="str", required=True),
        opsgenieApiKey=dict(type="str", required=True),
    ),
    NotificationType.PAGERDUTY: dict(
        pagerdutyAutoResolve=dict(type="str", required=False),
        pagerdutyIntegrationUrl=dict(type="str", required=False),
        pagerdutyPriority=dict(type="str", required=False),
        pagerdutyIntegrationKey=dict(type="str", required=True),
    ),
    NotificationType.PAGERTREE: dict(
        pagertreeAutoResolve=dict(type="str", required=False),
        pagertreeIntegrationUrl=dict(type="str", required=False),
        pagertreeUrgency=dict(type="str", required=False),
    ),
    NotificationType.PINGLET: dict(
        pingletPublishUrl=dict(type="str", required=True),
        pingletApiKey=dict(type="str", required=True),
    ),
    NotificationType.PLIVO: dict(
        plivoAuthID=dict(type="str", required=True),
        plivoAuthToken=dict(type="str", required=True),
        plivoMessageType=dict(type="str", required=False),
        plivoAnswerUrl=dict(type="str", required=False),
        plivoFromNumber=dict(type="str", required=True),
        plivoToNumber=dict(type="str", required=True),
    ),
    NotificationType.PROMOSMS: dict(
        promosmsAllowLongSMS=dict(type="bool", required=False),
        promosmsLogin=dict(type="str", required=True),
        promosmsPassword=dict(type="str", required=True),
        promosmsPhoneNumber=dict(type="str", required=True),
        promosmsSMSType=dict(type="str", required=False),
        promosmsSenderName=dict(type="str", required=False),
    ),
    NotificationType.PUMBLE: dict(
        webhookURL=dict(type="str", required=True),
    ),
    NotificationType.PUSHBULLET: dict(
        pushbulletAccessToken=dict(type="str", required=True),
    ),
    NotificationType.PUSHDEER: dict(
        pushdeerServer=dict(type="str", required=False),
        pushdeerKey=dict(type="str", required=True),
    ),
    NotificationType.PUSHOVER: dict(
        pushoveruserkey=dict(type="str", required=True),
        pushoverapptoken=dict(type="str", required=True),
        pushoversounds=dict(type="str", required=False),
        pushoverpriority=dict(type="str", required=False),
        pushovertitle=dict(type="str", required=False),
        pushoverdevice=dict(type="str", required=False),
        pushoverttl=dict(type="int", required=False),
        pushoversounds_up=dict(type="str", required=False),
    ),
    NotificationType.PUSHPLUS: dict(
        pushPlusSendKey=dict(type="str", required=True),
    ),
    NotificationType.PUSHY: dict(
        pushyAPIKey=dict(type="str", required=True),
        pushyToken=dict(type="str", required=True),
    ),
    NotificationType.RESEND: dict(
        resendApiKey=dict(type="str", required=True),
        resendFromEmail=dict(type="str", required=True),
        resendFromName=dict(type="str", required=False),
        resendToEmail=dict(type="str", required=True),
        resendSubject=dict(type="str", required=False),
    ),
    NotificationType.ROCKET_CHAT: dict(
        rocketchannel=dict(type="str", required=False),
        rocketusername=dict(type="str", required=False),
        rocketiconemo=dict(type="str", required=False),
        rocketwebhookURL=dict(type="str", required=True),
    ),
    NotificationType.SENDGRID: dict(
        sendgridApiKey=dict(type="str", required=True),
        sendgridToEmail=dict(type="str", required=True),
        sendgridCcEmail=dict(type="str", required=False),
        sendgridBccEmail=dict(type="str", required=False),
        sendgridFromEmail=dict(type="str", required=True),
        sendgridSubject=dict(type="str", required=False),
    ),
    NotificationType.SERVERCHAN: dict(
        serverChanSendKey=dict(type="str", required=True),
    ),
    NotificationType.SERWERSMS: dict(
        serwersmsUsername=dict(type="str", required=True),
        serwersmsPassword=dict(type="str", required=True),
        serwersmsSenderName=dict(type="str", required=False),
        serwersmsRecipientType=dict(type="str", required=False),
        serwersmsGroupId=dict(type="str", required=False),
        serwersmsPhoneNumber=dict(type="str", required=False),
    ),
    NotificationType.SEVENIO: dict(
        sevenioReceiver=dict(type="int", required=True),
        sevenioSender=dict(type="str", required=False),
        sevenioApiKey=dict(type="str", required=True),
    ),
    NotificationType.SIGNAL: dict(
        signalUseTemplate=dict(type="bool", required=False),
        signalTemplate=dict(type="str", required=False),
        signalNumber=dict(type="str", required=True),
        signalRecipients=dict(type="str", required=True),
        signalURL=dict(type="str", required=True),
    ),
    NotificationType.SIGNALGRID: dict(
        signalgridClientKey=dict(type="str", required=True),
        signalgridChannel=dict(type="str", required=True),
    ),
    NotificationType.SIGNL4: dict(
        webhookURL=dict(type="str", required=True),
    ),
    NotificationType.SLACK: dict(
        slackchannelnotify=dict(type="bool", required=False),
        slackchannel=dict(type="str", required=False),
        slackusername=dict(type="str", required=False),
        slackiconemo=dict(type="str", required=False),
        slackwebhookURL=dict(type="str", required=True),
        slackUseTemplate=dict(type="bool", required=False),
        slackTemplate=dict(type="str", required=False),
        slackIncludeGroupName=dict(type="bool", required=False),
        slackrichmessage=dict(type="bool", required=False),
    ),
    NotificationType.SMSGATEWAY: dict(
        smsgatewayUrl=dict(type="str", required=True),
        smsgatewayTo=dict(type="str", required=True),
        smsgatewayApiKey=dict(type="str", required=True),
    ),
    NotificationType.SMSPLANET: dict(
        smsplanetApiToken=dict(type="str", required=True),
        smsplanetSenderName=dict(type="str", required=False),
        smsplanetPhoneNumbers=dict(type="str", required=True),
    ),
    NotificationType.SMSC: dict(
        smscTranslit=dict(type="str", required=False),
        smscLogin=dict(type="str", required=True),
        smscPassword=dict(type="str", required=True),
        smscToNumber=dict(type="str", required=True),
        smscSenderName=dict(type="str", required=False),
    ),
    NotificationType.SMSEAGLE: dict(
        smseagleApiType=dict(type="str", required=False),
        smseagleRecipientType=dict(type="str", required=False),
        smseagleMsgType=dict(type="str", required=False),
        smseagleDuration=dict(type="int", required=False),
        smseagleTtsModel=dict(type="int", required=False),
        smseagleUrl=dict(type="str", required=True),
        smseagleToken=dict(type="str", required=True),
        smseagleRecipient=dict(type="str", required=False),
        smseagleEncoding=dict(type="bool", required=False),
        smseaglePriority=dict(type="int", required=False),
        smseagleRecipientContact=dict(type="str", required=False),
        smseagleRecipientGroup=dict(type="str", required=False),
        smseagleRecipientTo=dict(type="str", required=False),
    ),
    NotificationType.SMSIR: dict(
        smsirApiKey=dict(type="str", required=True),
        smsirNumber=dict(type="str", required=True),
        smsirTemplate=dict(type="str", required=True),
    ),
    NotificationType.SMSMANAGER: dict(
        smsmanagerApiKey=dict(type="str", required=False),
        numbers=dict(type="str", required=False),
        messageType=dict(type="str", required=False),
    ),
    NotificationType.SMSPARTNER: dict(
        smspartnerApikey=dict(type="str", required=True),
        smspartnerSenderName=dict(type="str", required=True),
        smspartnerPhoneNumber=dict(type="str", required=True),
    ),
    NotificationType.SMTP: dict(
        smtpHost=dict(type="str", required=True),
        smtpPort=dict(type="int", required=True),
        smtpSecure=dict(type="str", required=False),
        smtpIgnoreSTARTTLS=dict(type="bool", required=False),
        smtpIgnoreTLSError=dict(type="bool", required=False),
        smtpDkimDomain=dict(type="str", required=False),
        smtpDkimKeySelector=dict(type="str", required=False),
        smtpDkimPrivateKey=dict(type="str", required=False),
        smtpDkimHashAlgo=dict(type="str", required=False),
        smtpDkimheaderFieldNames=dict(type="str", required=False),
        smtpDkimskipFields=dict(type="str", required=False),
        smtpUsername=dict(type="str", required=False),
        smtpPassword=dict(type="str", required=False),
        smtpAdditionalHeaders=dict(type="str", required=False),
        customSubject=dict(type="str", required=False),
        customBody=dict(type="str", required=False),
        htmlBody=dict(type="bool", required=False),
        smtpFrom=dict(type="str", required=True),
        smtpCC=dict(type="str", required=False),
        smtpBCC=dict(type="str", required=False),
        smtpTo=dict(type="str", required=False),
    ),
    NotificationType.SPLUNK: dict(
        splunkAutoResolve=dict(type="str", required=False),
        splunkSeverity=dict(type="str", required=False),
        splunkRestURL=dict(type="str", required=True),
    ),
    NotificationType.SPUGPUSH: dict(
        templateKey=dict(type="str", required=True),
    ),
    NotificationType.SQUADCAST: dict(
        squadcastWebhookURL=dict(type="str", required=True),
    ),
    NotificationType.STACKFIELD: dict(
        stackfieldwebhookURL=dict(type="str", required=True),
    ),
    NotificationType.TEAMS: dict(
        webhookUrl=dict(type="str", required=True),
        teamsEnableTags=dict(type="bool", required=False),
    ),
    NotificationType.PUSHBYTECHULUS: dict(
        pushTitle=dict(type="str", required=False),
        pushTimeSensitive=dict(type="bool", required=False),
        pushChannel=dict(type="str", required=False),
        pushSound=dict(type="str", required=False),
        pushAPIKey=dict(type="str", required=True),
    ),
    NotificationType.TELEGRAM: dict(
        telegramServerUrl=dict(type="str", required=False),
        telegramChatID=dict(type="str", required=True),
        telegramSendSilently=dict(type="bool", required=False),
        telegramProtectContent=dict(type="bool", required=False),
        telegramMessageThreadID=dict(type="str", required=False),
        telegramUseTemplate=dict(type="bool", required=False),
        telegramTemplateParseMode=dict(type="str", required=False),
        telegramTemplate=dict(type="str", required=False),
        telegramBotToken=dict(type="str", required=True),
    ),
    NotificationType.TELNYX: dict(
        telnyxPhoneNumber=dict(type="str", required=True),
        telnyxToNumber=dict(type="str", required=True),
        telnyxMessagingProfileId=dict(type="str", required=False),
        telnyxApiKey=dict(type="str", required=True),
    ),
    NotificationType.TELTONIKA: dict(
        teltonikaUrl=dict(type="str", required=True),
        teltonikaUnsafeTls=dict(type="bool", required=False),
        teltonikaUsername=dict(type="str", required=True),
        teltonikaPassword=dict(type="str", required=True),
        teltonikaModem=dict(type="str", required=True),
        teltonikaPhoneNumber=dict(type="str", required=True),
    ),
    NotificationType.THREEMA: dict(
        threemaSenderIdentity=dict(type="str", required=True),
        threemaSecret=dict(type="str", required=True),
        threemaRecipientType=dict(type="str", required=True),
        threemaRecipient=dict(type="str", required=False),
    ),
    NotificationType.TURBOSMTP: dict(
        turbosmtpConsumerKey=dict(type="str", required=True),
        turbosmtpConsumerSecret=dict(type="str", required=True),
        turbosmtpRegion=dict(type="str", required=True),
        turbosmtpFromEmail=dict(type="str", required=True),
        turbosmtpToEmail=dict(type="str", required=True),
        turbosmtpSubject=dict(type="str", required=False),
        turbosmtpCcEmail=dict(type="str", required=False),
        turbosmtpBccEmail=dict(type="str", required=False),
    ),
    NotificationType.TWILIO: dict(
        twilioApiKey=dict(type="str", required=False),
        twilioAccountSID=dict(type="str", required=True),
        twilioAuthToken=dict(type="str", required=True),
        twilioToNumber=dict(type="str", required=True),
        twilioFromNumber=dict(type="str", required=True),
        twilioMessagingServiceSID=dict(type="str", required=False),
    ),
    NotificationType.VK: dict(
        vkAccessToken=dict(type="str", required=True),
        vkApiVersion=dict(type="str", required=True),
        vkPeerId=dict(type="str", required=True),
        vkDontParseLinks=dict(type="bool", required=False),
    ),
    NotificationType.VKTEAMS: dict(
        vkteamsBaseUrl=dict(type="str", required=True),
        vkteamsBotToken=dict(type="str", required=True),
        vkteamsChatId=dict(type="str", required=True),
        vkteamsUseTemplate=dict(type="bool", required=False),
        vkteamsTemplate=dict(type="str", required=False),
        vkteamsTemplateFormat=dict(type="str", required=False),
    ),
    NotificationType.WAHA: dict(
        wahaApiKey=dict(type="str", required=False),
        wahaSession=dict(type="str", required=True),
        wahaChatId=dict(type="str", required=True),
        wahaApiUrl=dict(type="str", required=True),
    ),
    NotificationType.WEBHOOK: dict(
        httpMethod=dict(type="str", required=False),
        webhookContentType=dict(type="str", required=False),
        webhookCustomBody=dict(type="str", required=False),
        webhookAdditionalHeaders=dict(type="str", required=False),
        webhookURL=dict(type="str", required=True),
    ),
    NotificationType.WECOM: dict(
        weComBotKey=dict(type="str", required=True),
        weComMentionedMobileList=dict(type="str", required=False),
    ),
    NotificationType.WHAPI: dict(
        whapiAuthToken=dict(type="str", required=True),
        whapiRecipient=dict(type="str", required=True),
        whapiApiUrl=dict(type="str", required=False),
    ),
    NotificationType.WPUSH: dict(
        wpushAPIkey=dict(type="str", required=True),
        wpushChannel=dict(type="str", required=True),
    ),
    NotificationType.WXPUSHER: dict(
        wxpusherSPT=dict(type="str", required=True),
    ),
    NotificationType.YZJ: dict(
        yzjWebHookUrl=dict(type="str", required=True),
        yzjToken=dict(type="str", required=True),
    ),
    NotificationType.ZOHOCLIQ: dict(
        webhookUrl=dict(type="str", required=True),
    ),
}

notification_provider_conditions = dict(
    amootPatternCodeId=dict(
        min=1,
    ),
    googleChatMaxRetries=dict(
        min=1,
        max=10,
    ),
    gotifyPriority=dict(
        min=0,
        max=10,
    ),
    jsmPriority=dict(
        min=1,
        max=5,
    ),
    ntfyPriority=dict(
        min=1,
        max=5,
    ),
    ntfyPriorityDown=dict(
        min=1,
        max=5,
    ),
    opsgeniePriority=dict(
        min=1,
        max=5,
    ),
    pushoverttl=dict(
        min=0,
    ),
    smseagleDuration=dict(
        min=0,
        max=30,
    ),
    smseaglePriority=dict(
        min=0,
        max=9,
    ),
    smtpPort=dict(
        min=0,
        max=65535,
    ),
)
