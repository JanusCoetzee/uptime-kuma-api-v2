from __future__ import annotations

import functools
import json
import threading
import time
from contextlib import contextmanager
from copy import deepcopy
from collections.abc import Iterator
from typing import Any

import socketio

from . import (
    Event,
    Timeout,
    UptimeKumaConnectionError,
    UptimeKumaException
)
from ._mixins.monitors import MonitorsMixin
from ._mixins.tags import TagsMixin
from ._mixins.notifications import NotificationsMixin
from ._mixins.proxies import ProxiesMixin
from ._mixins.status_pages import StatusPagesMixin
from ._mixins.heartbeats import HeartbeatsMixin
from ._mixins.settings import SettingsMixin
from ._mixins.auth import AuthMixin
from ._mixins.docker_hosts import DockerHostsMixin
from ._mixins.maintenance import MaintenanceMixin
from ._mixins.api_keys import ApiKeysMixin


def _locked(method):
    # the socketio background thread runs the _event_* handlers while the
    # caller thread reads the cache, so every cache update holds self._lock
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        with self._lock:
            return method(self, *args, **kwargs)
    return wrapper


class UptimeKumaApi(
    MonitorsMixin,
    TagsMixin,
    NotificationsMixin,
    ProxiesMixin,
    StatusPagesMixin,
    HeartbeatsMixin,
    SettingsMixin,
    AuthMixin,
    DockerHostsMixin,
    MaintenanceMixin,
    ApiKeysMixin,
    object,
):
    """This class is used to communicate with Uptime Kuma.

    Example:

    Import UptimeKumaApi from the library and specify the Uptime Kuma server url (e.g. 'http://127.0.0.1:3001'), username and password to initialize the connection.

        >>> from uptime_kuma_api import UptimeKumaApi
        >>> api = UptimeKumaApi('INSERT_URL')
        >>> api.login('INSERT_USERNAME', 'INSERT_PASSWORD')
        {
            'token': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6ImFkbWluIiwiaWF0IjoxNjgyOTU4OTU4fQ.Xb81nuKXeNyE1D_XoQowYgsgZHka-edONdwHmIznJdk'
        }

    Now you can call one of the existing methods of the instance. For example create a new monitor:

        >>> api.add_monitor(
        ...     type=MonitorType.HTTP,
        ...     name="Google",
        ...     url="https://google.com"
        ... )
        {
            'msg': 'Added Successfully.',
            'monitorId': 1
        }

    At the end, the connection to the API must be disconnected so that the program does not block.

        >>> api.disconnect()

    With a context manager, the disconnect method is called automatically:

    .. code-block:: python

        from uptime_kuma_api import UptimeKumaApi

        with UptimeKumaApi('INSERT_URL') as api:
            api.login('INSERT_USERNAME', 'INSERT_PASSWORD')
            api.add_monitor(
                type=MonitorType.HTTP,
                name="Google",
                url="https://google.com"
            )

    :param str url: The url to the Uptime Kuma instance. For example ``http://127.0.0.1:3001``
    :param float timeout: How many seconds the client should wait for the connection, an expected event or a server
                          response. Default is ``10``.
    :param dict headers: Headers that are passed to the socketio connection, defaults to None
    :param bool ssl_verify: ``True`` to verify SSL certificates, or ``False`` to skip SSL certificate
                            verification, allowing connections to servers with self signed certificates.
                            Default is ``True``.
    :param float wait_events: How many seconds the client should wait for the next event of the same type.
                              There is no way to determine when the last message of a certain type has arrived.
                              Therefore, a timeout is required. If no further message has arrived within this time,
                              it is assumed that it was the last message. Defaults is ``0.2``.
    :raises UptimeKumaConnectionError: When connection to server failed.
    """

    def __init__(
            self,
            url: str,
            timeout: float = 10,
            headers: dict = None,
            ssl_verify: bool = True,
            wait_events: float = 0.2
    ) -> None:
        self.url = url.rstrip("/")
        self.timeout = timeout
        self.headers = headers
        self.ssl_verify = ssl_verify
        self.wait_events = wait_events
        self.sio = socketio.Client(ssl_verify=ssl_verify)
        self._version = None
        self._lock = threading.RLock()

        self._event_data: dict = {
            Event.MONITOR_LIST: None,
            Event.NOTIFICATION_LIST: None,
            Event.PROXY_LIST: None,
            Event.STATUS_PAGE_LIST: None,
            Event.HEARTBEAT_LIST: None,
            Event.IMPORTANT_HEARTBEAT_LIST: None,
            Event.AVG_PING: None,
            Event.UPTIME: None,
            Event.INFO: None,
            Event.CERT_INFO: None,
            Event.DOCKER_HOST_LIST: None,
            Event.AUTO_LOGIN: None,
            Event.MAINTENANCE_LIST: None,
            Event.API_KEY_LIST: None
        }

        # counts the list updates received per event, see wait_for_event
        self._event_seq = {event: 0 for event in self._event_data}

        self.sio.on(Event.CONNECT, self._event_connect)
        self.sio.on(Event.DISCONNECT, self._event_disconnect)
        self.sio.on(Event.MONITOR_LIST, self._event_monitor_list)
        self.sio.on(Event.UPDATE_MONITOR_INTO_LIST, self._event_update_monitor_into_list)
        self.sio.on(Event.DELETE_MONITOR_FROM_LIST, self._event_delete_monitor_from_list)
        self.sio.on(Event.NOTIFICATION_LIST, self._event_notification_list)
        self.sio.on(Event.PROXY_LIST, self._event_proxy_list)
        self.sio.on(Event.STATUS_PAGE_LIST, self._event_status_page_list)
        self.sio.on(Event.HEARTBEAT_LIST, self._event_heartbeat_list)
        self.sio.on(Event.IMPORTANT_HEARTBEAT_LIST, self._event_important_heartbeat_list)
        self.sio.on(Event.AVG_PING, self._event_avg_ping)
        self.sio.on(Event.UPTIME, self._event_uptime)
        self.sio.on(Event.HEARTBEAT, self._event_heartbeat)
        self.sio.on(Event.INFO, self._event_info)
        self.sio.on(Event.CERT_INFO, self._event_cert_info)
        self.sio.on(Event.DOCKER_HOST_LIST, self._event_docker_host_list)
        self.sio.on(Event.AUTO_LOGIN, self._event_auto_login)
        self.sio.on(Event.INIT_SERVER_TIMEZONE, self._event_init_server_timezone)
        self.sio.on(Event.MAINTENANCE_LIST, self._event_maintenance_list)
        self.sio.on(Event.API_KEY_LIST, self._event_api_key_list)

        self.connect()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()

    @contextmanager
    def wait_for_event(self, event: Event, new: bool = False) -> Iterator[None]:
        # waits for the first event of the given type to arrive, or with
        # new=True for a new event to arrive after the body ran (for calls
        # after which the server pushes an updated list)
        seq = self._event_seq[event]
        yield
        timestamp = time.time()
        while (self._event_seq[event] == seq if new else self._event_data[event] is None):
            if time.time() - timestamp > self.timeout:
                raise Timeout(f"Timed out while waiting for event {event}")
            time.sleep(0.01)

    def _get_event_data(self, event) -> Any:
        monitor_events = [Event.AVG_PING, Event.UPTIME, Event.HEARTBEAT_LIST, Event.IMPORTANT_HEARTBEAT_LIST, Event.CERT_INFO, Event.HEARTBEAT]
        timestamp = time.time()
        while self._event_data[event] is None:
            if time.time() - timestamp > self.timeout:
                raise Timeout(f"Timed out while waiting for event {event}")
            # do not wait for events that are not sent
            if self._event_data[Event.MONITOR_LIST] == {} and event in monitor_events:
                return []
            time.sleep(0.01)
        time.sleep(self.wait_events)  # wait for multiple messages
        with self._lock:
            return deepcopy(self._event_data[event].copy())

    def _call(self, event, data=None) -> Any:
        try:
            r = self.sio.call(event, data, timeout=self.timeout)
        except socketio.exceptions.TimeoutError as e:
            raise Timeout(f"Timed out while calling {event}") from e
        except socketio.exceptions.SocketIOError as e:
            raise UptimeKumaException(f"Socket.IO error while calling {event}: {e}") from e
        if isinstance(r, dict) and "ok" in r:
            if not r["ok"]:
                raise UptimeKumaException(r.get("msg"))
            r.pop("ok")
        return r

    def _event_connect(self) -> None:
        pass

    def _event_disconnect(self) -> None:
        pass

    @_locked
    def _event_monitor_list(self, data) -> None:
        self._event_seq[Event.MONITOR_LIST] += 1
        self._event_data[Event.MONITOR_LIST] = data

    @_locked
    def _event_update_monitor_into_list(self, data) -> None:
        self._event_seq[Event.MONITOR_LIST] += 1
        # Kuma 2.x sends deltas instead of a full monitorList after changes
        if self._event_data[Event.MONITOR_LIST] is not None:
            self._event_data[Event.MONITOR_LIST].update(data)

    @_locked
    def _event_delete_monitor_from_list(self, monitor_id) -> None:
        self._event_seq[Event.MONITOR_LIST] += 1
        if self._event_data[Event.MONITOR_LIST] is not None:
            self._event_data[Event.MONITOR_LIST].pop(str(monitor_id), None)

    @_locked
    def _event_notification_list(self, data) -> None:
        self._event_seq[Event.NOTIFICATION_LIST] += 1
        self._event_data[Event.NOTIFICATION_LIST] = data

    @_locked
    def _event_proxy_list(self, data) -> None:
        self._event_seq[Event.PROXY_LIST] += 1
        self._event_data[Event.PROXY_LIST] = data

    @_locked
    def _event_status_page_list(self, data) -> None:
        self._event_seq[Event.STATUS_PAGE_LIST] += 1
        self._event_data[Event.STATUS_PAGE_LIST] = data

    @_locked
    def _event_heartbeat_list(self, monitor_id, data, overwrite) -> None:
        monitor_id = int(monitor_id)

        if self._event_data[Event.HEARTBEAT_LIST] is None:
            self._event_data[Event.HEARTBEAT_LIST] = {}
        if monitor_id not in self._event_data[Event.HEARTBEAT_LIST] or overwrite:
            self._event_data[Event.HEARTBEAT_LIST][monitor_id] = data
        else:
            self._event_data[Event.HEARTBEAT_LIST][monitor_id].append(data)

    @_locked
    def _event_important_heartbeat_list(self, monitor_id, data, overwrite) -> None:
        monitor_id = int(monitor_id)

        if self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] is None:
            self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] = {}
        if monitor_id not in self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] or overwrite:
            self._event_data[Event.IMPORTANT_HEARTBEAT_LIST][monitor_id] = data
        else:
            self._event_data[Event.IMPORTANT_HEARTBEAT_LIST][monitor_id].append(data)

    @_locked
    def _event_avg_ping(self, monitor_id, data) -> None:
        monitor_id = int(monitor_id)

        if self._event_data[Event.AVG_PING] is None:
            self._event_data[Event.AVG_PING] = {}
        self._event_data[Event.AVG_PING][monitor_id] = data

    @_locked
    def _event_uptime(self, monitor_id, type_, data) -> None:
        monitor_id = int(monitor_id)

        if self._event_data[Event.UPTIME] is None:
            self._event_data[Event.UPTIME] = {}
        if monitor_id not in self._event_data[Event.UPTIME]:
            self._event_data[Event.UPTIME][monitor_id] = {}
        self._event_data[Event.UPTIME][monitor_id][type_] = data

    @_locked
    def _event_heartbeat(self, data) -> None:
        if self._event_data[Event.HEARTBEAT_LIST] is None:
            self._event_data[Event.HEARTBEAT_LIST] = {}
        monitor_id = data["monitorID"]
        if monitor_id not in self._event_data[Event.HEARTBEAT_LIST]:
            self._event_data[Event.HEARTBEAT_LIST][monitor_id] = []
        self._event_data[Event.HEARTBEAT_LIST][monitor_id].append(data)
        if len(self._event_data[Event.HEARTBEAT_LIST][monitor_id]) > 150:
            self._event_data[Event.HEARTBEAT_LIST][monitor_id].pop(0)

        # add heartbeat to important heartbeat list
        if data["important"]:
            if self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] is None:
                self._event_data[Event.IMPORTANT_HEARTBEAT_LIST] = {}
            if monitor_id not in self._event_data[Event.IMPORTANT_HEARTBEAT_LIST]:
                self._event_data[Event.IMPORTANT_HEARTBEAT_LIST][monitor_id] = []
            self._event_data[Event.IMPORTANT_HEARTBEAT_LIST][monitor_id] = [data] + self._event_data[Event.IMPORTANT_HEARTBEAT_LIST][monitor_id]

    @_locked
    def _event_info(self, data) -> None:
        if "version" not in data:
            # wait for the info event that is sent after login and contains the version
            return
        self._version = None
        self._event_data[Event.INFO] = data

    @_locked
    def _event_cert_info(self, monitor_id, data) -> None:
        monitor_id = int(monitor_id)

        if self._event_data[Event.CERT_INFO] is None:
            self._event_data[Event.CERT_INFO] = {}
        self._event_data[Event.CERT_INFO][monitor_id] = json.loads(data)

    @_locked
    def _event_docker_host_list(self, data) -> None:
        self._event_seq[Event.DOCKER_HOST_LIST] += 1
        self._event_data[Event.DOCKER_HOST_LIST] = data

    @_locked
    def _event_auto_login(self) -> None:
        self._event_data[Event.AUTO_LOGIN] = True

    def _event_init_server_timezone(self) -> None:
        pass

    @_locked
    def _event_maintenance_list(self, data) -> None:
        self._event_seq[Event.MAINTENANCE_LIST] += 1
        self._event_data[Event.MAINTENANCE_LIST] = data

    @_locked
    def _event_api_key_list(self, data) -> None:
        self._event_seq[Event.API_KEY_LIST] += 1
        self._event_data[Event.API_KEY_LIST] = data

    def connect(self) -> None:
        """
        Connects to Uptime Kuma.

        Called automatically when the UptimeKumaApi instance is created.

        :raises UptimeKumaConnectionError: When connection to server failed.
        """
        try:
            self.sio.connect(f'{self.url}/socket.io/', wait_timeout=self.timeout, headers=self.headers)
        except Exception as e:
            raise UptimeKumaConnectionError("unable to connect") from e

    def disconnect(self) -> None:
        """
        Disconnects from Uptime Kuma.

        Needs to be called to prevent blocking the program.
        """
        self.sio.disconnect()

    @property
    def version(self) -> str:
        # read the cached INFO directly: info() sleeps wait_events on every call
        if self._version is None:
            timestamp = time.time()
            while self._event_data[Event.INFO] is None:
                if time.time() - timestamp > self.timeout:
                    raise Timeout(f"Timed out while waiting for event {Event.INFO}")
                time.sleep(0.01)
            self._version = self._event_data[Event.INFO].get("version")
        return self._version
