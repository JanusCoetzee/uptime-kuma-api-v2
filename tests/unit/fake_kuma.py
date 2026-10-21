"""An offline stand-in for the Socket.IO client, used by the unit tests.

``make_api`` builds a real ``UptimeKumaApi`` whose ``sio`` is a ``FakeSio``.
Requests are recorded in ``FakeSio.calls`` and answered from ``replies``;
change requests also count as a pushed list update of the right list, like
the real server does (see ``PUSHES``), so ``wait_for_event(..., new=True)``
returns.
"""
import copy
import warnings
from unittest import mock

from uptime_kuma_client import Event, UptimeKumaApi


# The list event the real server pushes after each change request.
PUSHES = {
    "add": Event.MONITOR_LIST,
    "editMonitor": Event.MONITOR_LIST,
    "addNotification": Event.NOTIFICATION_LIST,
    "addProxy": Event.PROXY_LIST,
    "addDockerHost": Event.DOCKER_HOST_LIST,
    "addAPIKey": Event.API_KEY_LIST,
    "enableAPIKey": Event.API_KEY_LIST,
    "disableAPIKey": Event.API_KEY_LIST,
}


class FakeSio:
    def __init__(self):
        self.calls = []
        self.replies = {}
        self.handlers = {}
        self.connected = False
        self.connect_error = None
        self.api = None

    def on(self, event, handler):
        self.handlers[event] = handler

    def connect(self, url, wait_timeout=None, headers=None):
        if self.connect_error:
            raise self.connect_error
        self.connected = True
        self.connect_args = (url, wait_timeout, headers)

    def disconnect(self):
        self.connected = False

    def call(self, event, data=None, timeout=None):
        self.calls.append((event, data))
        if self.api is not None and event in PUSHES:
            self.api._event_seq[PUSHES[event]] += 1
        reply = self.replies.get(event, {"ok": True})
        if isinstance(reply, Exception):
            raise reply
        if callable(reply):
            reply = reply(data)
        return copy.deepcopy(reply)

    def sent(self, event):
        """The payloads sent for one event name."""
        return [data for name, data in self.calls if name == event]


def make_api(url="http://kuma.test/", quiet=True, **kwargs):
    kwargs.setdefault("timeout", 0.3)
    kwargs.setdefault("wait_events", 0)
    sio = FakeSio()
    client = "uptime_kuma_client.api.socketio.Client"
    with mock.patch(client, return_value=sio):
        with warnings.catch_warnings():
            if quiet:
                # the fake host is plain http on purpose, see TestInsecureUrl
                warnings.simplefilter("ignore", UserWarning)
            api = UptimeKumaApi(url, **kwargs)
    sio.api = api
    api._event_data[Event.INFO] = {"version": "2.5.6"}
    return api
