from __future__ import annotations

import inspect
import ipaddress
import logging
from urllib.parse import urlsplit

from .monitor_status import MonitorStatus


def int_to_bool(data, keys) -> None:
    if isinstance(data, list):
        for d in data:
            int_to_bool(d, keys)
    else:
        for key in keys:
            if key in data:
                data[key] = True if data[key] == 1 else False


# callers filter on this name; it changed in the 2.0.0 rename (see CHANGELOG)
logger = logging.getLogger("uptime_kuma_client.api")
_warned_values: set[tuple] = set()


def parse_value(data, key, type_, default=None) -> None:
    if not data:
        return
    if isinstance(data, list):
        for d in data:
            parse_value(d, key, type_, default)
    else:
        if key in data:
            if data[key] is not None:
                try:
                    data[key] = type_(data[key])
                except ValueError:
                    # keep the raw value, but tell the user once per value
                    if (key, data[key]) not in _warned_values:
                        _warned_values.add((key, data[key]))
                        logger.warning(
                            "Unknown %s value %r (not a %s); keeping the raw "
                            "value. The server may be newer than this "
                            "library.",
                            key, data[key], type_.__name__)
            elif default is not None:
                data[key] = default


# monitor
def parse_monitor_status(data) -> None:
    parse_value(data, "status", MonitorStatus)


def _check_missing_arguments(required_params, kwargs) -> None:
    missing_arguments = []
    for required_param in required_params:
        if kwargs.get(required_param) is None:
            missing_arguments.append(required_param)
    if missing_arguments:
        missing_arguments_str = ", ".join(
            [f"'{i}'" for i in missing_arguments])
        raise TypeError(
            f"missing {len(missing_arguments)} required argument: "
            f"{missing_arguments_str}")


def _check_argument_conditions(valid_params, kwargs) -> None:
    for valid_param in valid_params:
        if valid_param in kwargs:
            value = kwargs[valid_param]
            if value is None:
                continue
            conditions = valid_params[valid_param]
            min_ = conditions.get("min")
            max_ = conditions.get("max")
            if min_ is not None and value < min_:
                raise ValueError(
                    f"the value of {valid_param} must not be less "
                    f"than {min_}")
            if max_ is not None and value > max_:
                raise ValueError(
                    f"the value of {valid_param} must not be larger "
                    f"than {max_}")


def _is_loopback_host(host: str | None) -> bool:
    """True for ``localhost`` and loopback IP addresses (127.0.0.0/8, ::1).

    Other names are not resolved, so they count as remote.
    """
    if not host:
        return False
    host = host.lower().rstrip(".")
    if host == "localhost":
        return True
    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        return False
    # ::ffff:127.0.0.1 is loopback; older Pythons do not say so themselves
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped:
        address = address.ipv4_mapped
    return address.is_loopback


def _sends_credentials_in_clear(url: str) -> bool:
    """True if ``url`` is unencrypted (http/ws) and not a loopback host."""
    parts = urlsplit(url)
    return parts.scheme.lower() in ("http", "ws") and not _is_loopback_host(
        parts.hostname)


def _check_edit_arguments(
        method: str, kwargs: dict, builder, current: dict,
        extra=()) -> None:
    """Reject keyword arguments of an ``edit_*`` call that ``add_*`` would.

    An edit starts from the object the server returned, so besides the
    parameters of the ``add_*`` builder it accepts the fields of that object
    (a round trip of ``get_*`` into ``edit_*`` keeps working) and ``extra``.
    """
    params = inspect.signature(builder).parameters.values()
    allowed = {p.name for p in params if p.kind is not p.VAR_KEYWORD}
    allowed.update(current, extra)
    for key in kwargs:
        if key not in allowed:
            raise TypeError(
                f"{method}() got an unexpected keyword argument '{key}'")
