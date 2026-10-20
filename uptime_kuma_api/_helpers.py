from __future__ import annotations

import logging

from . import (
    MonitorStatus
)


def int_to_bool(data, keys) -> None:
    if isinstance(data, list):
        for d in data:
            int_to_bool(d, keys)
    else:
        for key in keys:
            if key in data:
                data[key] = True if data[key] == 1 else False


# keep the pre-split name: callers filter on it
logger = logging.getLogger("uptime_kuma_api.api")
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
                            "value. The server may be newer than this library.",
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
        missing_arguments_str = ", ".join([f"'{i}'" for i in missing_arguments])
        raise TypeError(f"missing {len(missing_arguments)} required argument: {missing_arguments_str}")


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
                raise ValueError(f"the value of {valid_param} must not be less than {min_}")
            if max_ is not None and value > max_:
                raise ValueError(f"the value of {valid_param} must not be larger than {max_}")
