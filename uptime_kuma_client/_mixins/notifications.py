from __future__ import annotations

import json

from ..event import Event
from ..exceptions import UptimeKumaException
from ..notification_providers import (
    NotificationType,
    notification_provider_conditions,
    notification_provider_options,
)
from ..docstrings import (
    append_docstring,
    notification_docstring
)
from .._helpers import (
    _check_argument_conditions,
    _check_missing_arguments,
    parse_value,
)
from ._base import MixinBase


# notification
def parse_notification_type(data) -> None:
    parse_value(data, "type", NotificationType)


def _build_notification_data(
    name: str,
    type: NotificationType,
    isDefault: bool = False,
    applyExisting: bool = False,
    **kwargs
) -> dict:
    allowed_kwargs: list[str] = []
    for keys in notification_provider_options.values():
        allowed_kwargs.extend(keys)

    for key in kwargs.keys():
        if key not in allowed_kwargs:
            raise TypeError(f"unknown argument '{key}'")

    data = {
        "name": name,
        "type": type,
        "isDefault": isDefault,
        "applyExisting": applyExisting,
        **kwargs
    }
    return data


def _check_arguments_notification(kwargs) -> None:
    required_args = ["type", "name"]
    _check_missing_arguments(required_args, kwargs)

    type_ = kwargs["type"]
    required_args = [
        i for i, j in notification_provider_options[type_].items()
        if j["required"]]
    _check_missing_arguments(required_args, kwargs)
    _check_argument_conditions(notification_provider_conditions, kwargs)


class NotificationsMixin(MixinBase):
    def get_notifications(self) -> list[dict]:
        """
        Get all notifications.

        :return: All notifications.
        :rtype: list

        Example::

            >>> api.get_notifications()
            [
                {
                    'active': True,
                    'applyExisting': True,
                    'id': 1,
                    'isDefault': True,
                    'name': 'notification 1',
                    'pushAPIKey': '123456789',
                    'type': <NotificationType.PUSHBYTECHULUS: 'PushByTechulus'>
                    'userId': 1
                }
            ]
        """
        notifications = self._get_event_data(Event.NOTIFICATION_LIST)
        r = []
        for notification_raw in notifications:
            notification = notification_raw.copy()
            config = json.loads(notification["config"])
            del notification["config"]
            notification.update(config)
            r.append(notification)
        parse_notification_type(r)
        return r

    def get_notification(self, id_: int) -> dict:
        """
        Get a notification.

        :param int id_: Id of the notification to get.
        :return: The notification.
        :rtype: dict
        :raises UptimeKumaException: If the notification does not exist.

        Example::

            >>> api.get_notification(1)
            {
                'active': True,
                'applyExisting': True,
                'id': 1,
                'isDefault': True,
                'name': 'notification 1',
                'pushAPIKey': '123456789',
                'type': <NotificationType.PUSHBYTECHULUS: 'PushByTechulus'>
                'userId': 1
            }
        """
        notifications = self.get_notifications()
        for notification in notifications:
            if notification["id"] == id_:
                return notification
        raise UptimeKumaException("notification does not exist")

    @append_docstring(notification_docstring("test"))
    def test_notification(self, **kwargs) -> dict:
        """
        Test a notification.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.test_notification(
            ...     name="notification 1",
            ...     isDefault=True,
            ...     applyExisting=True,
            ...     type=NotificationType.PUSHBYTECHULUS,
            ...     pushAPIKey="INSERT_PUSH_API_KEY"
            ... )
            {
                'ok': True,
                'msg': 'Sent Successfully.'
            }
        """
        data = _build_notification_data(**kwargs)

        _check_arguments_notification(data)
        return self._call('testNotification', data)

    @append_docstring(notification_docstring("add"))
    def add_notification(self, **kwargs) -> dict:
        """
        Add a notification.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_notification(
            ...     name="notification 1",
            ...     isDefault=True,
            ...     applyExisting=True,
            ...     type=NotificationType.PUSHBYTECHULUS,
            ...     pushAPIKey="123456789"
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        data = _build_notification_data(**kwargs)

        _check_arguments_notification(data)
        with self.wait_for_event(Event.NOTIFICATION_LIST, new=True):
            return self._call('addNotification', (data, None))

    @append_docstring(notification_docstring("edit"))
    def edit_notification(self, id_: int, **kwargs) -> dict:
        """
        Edit a notification.

        :param int id_: Id of the notification to edit.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_notification(1,
            ...     name="notification 1 edited",
            ...     isDefault=False,
            ...     applyExisting=False,
            ...     type=NotificationType.PUSHDEER,
            ...     pushdeerKey="987654321"
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        notification = self.get_notification(id_)

        # remove old notification provider options from notification object
        if "type" in kwargs and kwargs["type"] != notification["type"]:
            for provider in notification_provider_options:
                provider_options = notification_provider_options[provider]
                if provider != kwargs["type"]:
                    for option in provider_options:
                        if option in notification:
                            del notification[option]

        notification.update(kwargs)
        _check_arguments_notification(notification)
        with self.wait_for_event(Event.NOTIFICATION_LIST, new=True):
            return self._call('addNotification', (notification, id_))

    def delete_notification(self, id_: int) -> dict:
        """
        Delete a notification.

        :param int id_: Id of the notification to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_notification(1)
            {
                'msg': 'Deleted'
            }
        """
        with self.wait_for_event(Event.NOTIFICATION_LIST):
            if id_ not in [i["id"] for i in self.get_notifications()]:
                raise UptimeKumaException("notification does not exist")
            return self._call('deleteNotification', id_)

    def check_apprise(self) -> bool:
        """
        Check if apprise exists.

        :return: The server response.
        :rtype: bool
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.check_apprise()
            True
        """
        return self._call('checkApprise')
