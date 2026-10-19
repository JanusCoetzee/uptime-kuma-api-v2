"""An offline stand-in for the Socket.IO client, used by the unit tests.

``make_api`` builds a real ``UptimeKumaApi`` whose ``sio`` is a ``FakeSio``.
Requests are recorded in ``FakeSio.calls`` and answered from ``replies``;
every request also counts as a pushed list update, like the real server does
after a change, so ``wait_for_event(..., new=True)`` returns.
"""
import copy
from unittest import mock

from uptime_kuma_api import Event, UptimeKumaApi


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
        if self.api is not None:
            for name in self.api._event_seq:
                self.api._event_seq[name] += 1
        reply = self.replies.get(event, {"ok": True})
        if isinstance(reply, Exception):
            raise reply
        if callable(reply):
            reply = reply(data)
        return copy.deepcopy(reply)

    def sent(self, event):
        """The payloads sent for one event name."""
        return [data for name, data in self.calls if name == event]


def make_api(**kwargs):
    kwargs.setdefault("timeout", 0.3)
    kwargs.setdefault("wait_events", 0)
    sio = FakeSio()
    with mock.patch("uptime_kuma_api.api.socketio.Client", return_value=sio):
        api = UptimeKumaApi("http://kuma.test/", **kwargs)
    sio.api = api
    api._event_data[Event.INFO] = {"version": "2.5.6"}
    return api
