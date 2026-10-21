import json
import re
from pathlib import Path

from bs4 import BeautifulSoup

from utils import (
    KUMA_SRC, deduplicate_list, require_titles, write_to_file,
    type_html_to_py
)


# deprecated or wrong inputs
ignored_inputs = {
    "slack": [
        "slackbutton"
    ],
    "rocket.chat": [
        "rocketbutton"
    ],
    "octopush": [
        "octopushDMLogin",
        "octopushDMAPIKey",
        "octopushDMPhoneNumber",
        "octopushDMSenderName",
        "octopushDMSMSType"
    ],
    "Splunk": [
        "pagerdutyIntegrationKey"
    ],
    # legacy or internal values with no form field of their own
    "Whatsapp360messenger": [
        "Whatsapp360messengerGroupId"  # superseded by ...GroupIds
    ],
    "Webpush": [
        "subscription"  # set by the browser subscribe button
    ],
    "discord": [
        # legacy flag, replaced by discordMessageFormat
        "discordUseMessageTemplate"
    ],
    "fluxer": [
        "fluxerUseMessageTemplate"
    ]
}

CONDITIONAL_ATTRS = ("v-if", "v-else-if", "v-else", "v-show")


def is_conditional(tag):
    """True if the form only shows the input under some condition.

    The API must then not demand it.
    """
    return any(
        a in node.attrs
        for node in [tag, *tag.parents]
        for a in CONDITIONAL_ATTRS
    )

titles = {
    "alerta": "Alerta",
    "AlertNow": "AlertNow",
    "apprise": "Apprise (Support 50+ Notification services)",
    "Bark": "Bark",
    "clicksendsms": "ClickSend SMS",
    "discord": "Discord",
    "GoogleChat": "Google Chat (Google Workspace)",
    "gorush": "Gorush",
    "gotify": "Gotify",
    "HomeAssistant": "Home Assistant",
    "Kook": "Kook",
    "line": "LINE Messenger",
    "LineNotify": "LINE Notify",
    "lunasea": "LunaSea",
    "matrix": "Matrix",
    "mattermost": "Mattermost",
    "ntfy": "Ntfy",
    "octopush": "Octopush",
    "OneBot": "OneBot",
    "Opsgenie": "Opsgenie",
    "PagerDuty": "PagerDuty",
    "PagerTree": "PagerTree",
    "pushbullet": "Pushbullet",
    "PushByTechulus": "Push by Techulus",
    "pushover": "Pushover",
    "pushy": "Pushy",
    "rocket.chat": "Rocket.Chat",
    "signal": "Signal",
    "slack": "Slack",
    "squadcast": "SquadCast",
    "SMSEagle": "SMSEagle",
    "smtp": "Email (SMTP)",
    "stackfield": "Stackfield",
    "teams": "Microsoft Teams",
    "telegram": "Telegram",
    "twilio": "Twilio",
    "Splunk": "Splunk",
    "webhook": "Webhook",
    "GoAlert": "GoAlert",
    "ZohoCliq": "ZohoCliq",
    "AliyunSMS": "AliyunSMS",
    "DingDing": "DingDing",
    "Feishu": "Feishu",
    "FreeMobile": "FreeMobile (mobile.free.fr)",
    "PushDeer": "PushDeer",
    "promosms": "PromoSMS",
    "serwersms": "SerwerSMS.pl",
    "SMSManager": "SmsManager (smsmanager.cz)",
    "WeCom": "WeCom",
    "ServerChan": "ServerChan",
    "nostr": "Nostr",
    "FlashDuty": "FlashDuty",
    "smsc": "SMSC",
    "Whatsapp360messenger": "WhatsApp (360messenger)",
}


def scrape_titles():
    """Provider titles from Kuma's own notification dialog (and en.json)."""
    with open(KUMA_SRC / "src/components/NotificationDialog.vue") as f:
        dialog = f.read()
    with open(KUMA_SRC / "src/lang/en.json") as f:
        lang = json.load(f)
    start = dialog.index("notificationNameList() {")
    body = dialog[start:dialog.index("\n        },", start)]
    found = {}
    pattern = (
        r'^\s*"?([\w.\-]+)"?:\s*'
        r'(?:"([^"]*)"|this\.\$t\("([^"]*)"\)),?\s*$')
    for m in re.finditer(pattern, body, re.MULTILINE):
        key, text, i18n = m.groups()
        found[key] = text if text is not None else lang.get(i18n, i18n)
    return found


def build_notification_providers():
    root = KUMA_SRC
    providers = {}
    found = []
    orphans = []
    all_titles = {**scrape_titles(), **titles}

    # get providers and input names
    for path in sorted(Path(root).glob('server/notification-providers/*')):
        with open(path) as f:
            content = f.read()
        match = re.search(
            r'class [^ ]+ extends NotificationProvider {', content)
        if match:
            match = re.search(r'name = "([^"]+)";', content)
            name = match.group(1)
            found.append(name)

            inputs = re.findall(r'notification\??\.([^ ,.;})\]?]+)', content)
            inputs = deduplicate_list(inputs)
            inputs = [i.strip() for i in inputs]

            providers[name] = {
                "title": all_titles.get(name),
                "inputs": {},
            }
            for input_ in inputs:
                if input_ not in ignored_inputs.get(name, []):
                    providers[name]["inputs"][input_] = {}

    require_titles(
        "notification providers", found, all_titles,
        "build_notifications.py")

    # get inputs
    for path in sorted(Path(root).glob('src/components/notifications/*')):
        if path.name == "index.js":
            continue
        with open(path) as f:
            content = f.read()
        match = re.search(
            r'<template>[\s\S]+</template>', content, re.MULTILINE)
        html = match.group(0)
        soup = BeautifulSoup(html, "html.parser")
        inputs = [
            t for t in soup.find_all(True)
            if any(k.startswith("v-model") for k in t.attrs)]
        for input_ in inputs:
            conditions = {}
            attrs = input_.attrs
            v_model = next(
                v for k, v in attrs.items() if k.startswith("v-model"))

            match = re.match(r'\$parent.notification.(.*)$', v_model)
            if match is None:
                # local UI state (for example a toggle), not a
                # notification field
                continue
            param_name = match.group(1)

            type_ = attrs.get("type")
            type_ = type_html_to_py(type_)

            required_true_values = ['', 'true']
            if (attrs.get("required") in required_true_values
                    or attrs.get(":required") in required_true_values):
                required = True
            else:
                required = False
            if is_conditional(input_):
                required = False

            min_ = attrs.get("min")
            if min_:
                conditions["min"] = int(min_)

            max_ = attrs.get("max")
            if max_:
                conditions["max"] = int(max_)

            # find provider inputs dict
            input_found = False
            for name in list(providers.keys()):
                inputs = providers[name]["inputs"]
                for provider_input in inputs:
                    if provider_input == param_name:
                        input_found = True
                        providers[name]["inputs"][provider_input] = {
                            "conditions": conditions,
                            "type": type_,
                            "required": required
                        }
            if not input_found:
                orphans.append(f"{path.name}: {param_name}")
    if orphans:
        raise SystemExit(
            "build_notifications.py: form inputs no provider reads (fix the "
            "scraping, or the provider if it should read them):\n  "
            + "\n  ".join(orphans)
        )
    return providers


notification_providers = build_notification_providers()

no_form_field = [
    f"{provider}: {name}"
    for provider, data in notification_providers.items()
    for name, spec in data["inputs"].items()
    if "conditions" not in spec
]
if no_form_field:
    raise SystemExit(
        "build_notifications.py: provider code reads inputs that have no form "
        "field (add them to 'ignored_inputs' if they are internal):\n  "
        + "\n  ".join(no_form_field)
    )

notification_provider_conditions = {}
for notification_provider in notification_providers:
    provider_inputs = notification_providers[notification_provider]["inputs"]
    for input_name, provider_input in provider_inputs.items():
        if provider_input["conditions"]:
            notification_provider_conditions[input_name] = (
                provider_input["conditions"])

write_to_file(
    "notification_providers.py.j2",
    "uptime_kuma_api/notification_providers.py",
    notification_providers=notification_providers,
    notification_provider_conditions=notification_provider_conditions
)
