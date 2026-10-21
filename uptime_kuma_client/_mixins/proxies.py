from __future__ import annotations

from ..event import Event
from ..exceptions import UptimeKumaException
from ..proxy_protocol import ProxyProtocol
from ..docstrings import (
    append_docstring,
    proxy_docstring
)
from .._helpers import (
    _check_argument_conditions,
    _check_edit_arguments,
    _check_missing_arguments,
    int_to_bool,
    parse_value,
)
from ._base import MixinBase


# proxy
def parse_proxy_protocol(data) -> None:
    parse_value(data, "protocol", ProxyProtocol)


def _build_proxy_data(
    protocol: ProxyProtocol,
    host: str,
    port: str,
    auth: bool = False,
    username: str | None = None,
    password: str | None = None,
    active: bool = True,
    default: bool = False,
    applyExisting: bool = False,
) -> dict:
    data = {
        "protocol": protocol,
        "host": host,
        "port": port,
        "auth": auth,
        "username": username,
        "password": password,
        "active": active,
        "default": default,
        "applyExisting": applyExisting
    }
    return data


def _check_arguments_proxy(kwargs) -> None:
    required_args = ["protocol", "host", "port"]
    if kwargs.get("auth"):
        required_args.extend(["username", "password"])
    _check_missing_arguments(required_args, kwargs)

    conditions = dict(
        port=dict(
            min=0,
            max=65535,
        )
    )
    _check_argument_conditions(conditions, kwargs)


class ProxiesMixin(MixinBase):
    def get_proxies(self) -> list[dict]:
        """
        Get all proxies.

        :return: All proxies.
        :rtype: list

        Example::

            >>> api.get_proxies()
            [
                {
                    'active': True,
                    'auth': True,
                    'createdDate': '2022-12-15 16:24:24',
                    'default': False,
                    'host': '127.0.0.1',
                    'id': 1,
                    'password': 'password',
                    'port': 8080,
                    'protocol': <ProxyProtocol.HTTP: 'http'>,
                    'userId': 1,
                    'username': 'username'
                }
            ]
        """
        r = self._get_event_data(Event.PROXY_LIST)
        int_to_bool(r, ["auth", "active", "default", "applyExisting"])
        parse_proxy_protocol(r)
        return r

    def get_proxy(self, id_: int) -> dict:
        """
        Get a proxy.

        :param int id_: Id of the proxy to get.
        :return: The proxy.
        :rtype: dict
        :raises UptimeKumaException: If the proxy does not exist.

        Example::

            >>> api.get_proxy(1)
            {
                'active': True,
                'auth': True,
                'createdDate': '2022-12-15 16:24:24',
                'default': False,
                'host': '127.0.0.1',
                'id': 1,
                'password': 'password',
                'port': 8080,
                'protocol': 'http',
                'userId': 1,
                'username': 'username'
            }
        """
        proxies = self.get_proxies()
        for proxy in proxies:
            if proxy.get("id") == id_:
                return proxy
        raise UptimeKumaException("proxy does not exist")

    @append_docstring(proxy_docstring("add"))
    def add_proxy(self, **kwargs) -> dict:
        """
        Add a proxy.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_proxy(
            ...     protocol=ProxyProtocol.HTTP,
            ...     host="127.0.0.1",
            ...     port=8080,
            ...     auth=True,
            ...     username="username",
            ...     password="password",
            ...     active=True,
            ...     default=False,
            ...     applyExisting=False
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        data = _build_proxy_data(**kwargs)

        _check_arguments_proxy(data)
        with self.wait_for_event(Event.PROXY_LIST, new=True):
            return self._call('addProxy', (data, None))

    @append_docstring(proxy_docstring("edit"))
    def edit_proxy(self, id_: int, **kwargs) -> dict:
        """
        Edit a proxy.

        :param int id_: Id of the proxy to edit.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_proxy(1,
            ...     protocol=ProxyProtocol.HTTPS,
            ...     host="127.0.0.2",
            ...     port=8888
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        proxy = self.get_proxy(id_)
        _check_edit_arguments(
            "edit_proxy", kwargs, _build_proxy_data, proxy)
        proxy.update(kwargs)
        _check_arguments_proxy(proxy)
        with self.wait_for_event(Event.PROXY_LIST, new=True):
            return self._call('addProxy', (proxy, id_))

    def delete_proxy(self, id_: int) -> dict:
        """
        Delete a proxy.

        :param int id_: Id of the proxy to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_proxy(1)
            {
                'msg': 'Deleted'
            }
        """
        with self.wait_for_event(Event.PROXY_LIST):
            if id_ not in [i["id"] for i in self.get_proxies()]:
                raise UptimeKumaException("proxy does not exist")
            return self._call('deleteProxy', id_)
