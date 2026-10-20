from __future__ import annotations

from .. import (
    Event,
    UptimeKumaException
)
from ..docstrings import (
    append_docstring,
    tag_docstring
)
from .._helpers import _check_missing_arguments
from ._base import MixinBase


def _build_tag_data(
    name: str,
    color: str
) -> dict:
    data = {
        "new": True,
        "name": name,
        "color": color
    }
    return data


def _check_arguments_tag(kwargs) -> None:
    required_args = [
        "name",
        "color"
    ]
    _check_missing_arguments(required_args, kwargs)


class TagsMixin(MixinBase):
    def _refresh_monitor_cache(self, monitor_id: int) -> None:
        # the monitor list event does not send the updated tags
        # store the raw response: get_monitor() converts it, the cache is raw
        if self._event_data[Event.MONITOR_LIST] is None:
            return
        monitor = self._call('getMonitor', monitor_id)["monitor"]
        with self._lock:
            if self._event_data[Event.MONITOR_LIST] is not None:
                self._event_data[Event.MONITOR_LIST][str(monitor_id)] = monitor

    def add_monitor_tag(self, tag_id: int, monitor_id: int, value: str = "") -> dict:
        """
        Add a tag to a monitor.

        :param int tag_id: Id of the tag.
        :param int monitor_id: Id of the monitor to add the tag to.
        :param str, optional value: Value of the tag., defaults to ""
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_monitor_tag(
            ...     tag_id=1,
            ...     monitor_id=1,
            ...     value="test"
            ... )
            {
                'msg': 'Added Successfully.'
            }
        """
        r = self._call('addMonitorTag', (tag_id, monitor_id, value))
        self._refresh_monitor_cache(monitor_id)
        return r

    def delete_monitor_tag(self, tag_id: int, monitor_id: int, value: str = "") -> dict:
        """
        Delete a tag from a monitor.

        :param int tag_id: Id of the tag to remove.
        :param int monitor_id: Id of monitor to remove the tag from.
        :param str, optional value: Value of the tag., defaults to ""
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_monitor_tag(
            ...     tag_id=1,
            ...     monitor_id=1,
            ...     value="test"
            ... )
            {
                'msg': 'Deleted Successfully.'
            }
        """
        with self.wait_for_event(Event.MONITOR_LIST):
            tags = [
                {
                    "monitor_id": y["monitor_id"],
                    "tag_id": y["tag_id"],
                    "value": y["value"]
                } for x in [
                    i.get("tags") for i in self.get_monitors()
                ] for y in x or []
            ]
            if {"monitor_id": monitor_id, "tag_id": tag_id, "value": value} not in tags:
                raise UptimeKumaException("monitor tag does not exist")
            r = self._call('deleteMonitorTag', (tag_id, monitor_id, value))
            self._refresh_monitor_cache(monitor_id)
            return r

    def get_tags(self) -> list[dict]:
        """
        Get all tags.

        :return: All tags.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_tags()
            [
                {
                    'color': '#ffffff',
                    'id': 1,
                    'name': 'tag 1'
                }
            ]
        """
        return self._call('getTags')["tags"]

    def get_tag(self, id_: int) -> dict:
        """
        Get a tag.

        :param int id_: Id of the monitor to get.
        :return: The tag.
        :rtype: dict
        :raises UptimeKumaException: If the tag does not exist.

        Example::

            >>> api.get_tag(1)
            {
                'color': '#ffffff',
                'id': 1,
                'name': 'tag 1'
            }
        """

        tags = self.get_tags()
        for tag in tags:
            if tag["id"] == id_:
                return tag
        raise UptimeKumaException("tag does not exist")

    @append_docstring(tag_docstring("add"))
    def add_tag(self, **kwargs) -> dict:
        """
        Add a tag.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_tag(
            ...     name="tag 1",
            ...     color="#ffffff"
            ... )
            {
                'color': '#ffffff',
                'id': 1,
                'name': 'tag 1'
            }
        """
        data = _build_tag_data(**kwargs)
        _check_arguments_tag(data)
        return self._call('addTag', data)["tag"]

    @append_docstring(tag_docstring("edit"))
    def edit_tag(self, id_: int, **kwargs) -> dict:
        """
        Edits an existing tag.

        :param int id_: Id of the tag to edit.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_tag(1,
            ...     name="tag 1 new",
            ...     color="#000000"
            ... )
            {
                'msg': 'Saved',
                'tag': {
                    'id': 1,
                    'name': 'tag 1 new',
                    'color': '#000000'
                }
            }
        """
        data = self.get_tag(id_)
        data.update(kwargs)
        _check_arguments_tag(data)
        return self._call('editTag', data)

    def delete_tag(self, id_: int) -> dict:
        """
        Delete a tag.

        :param int id_: Id of the monitor to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_tag(1)
            {
                'msg': 'Deleted Successfully.'
            }
        """
        if id_ not in [i["id"] for i in self.get_tags()]:
            raise UptimeKumaException("tag does not exist")
        return self._call('deleteTag', id_)
