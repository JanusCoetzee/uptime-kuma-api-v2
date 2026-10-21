from __future__ import annotations

from .. import (
    Event,
    UptimeKumaException
)
from .._helpers import int_to_bool
from ._base import MixinBase


class ApiKeysMixin(MixinBase):
    def get_api_keys(self) -> list[dict]:
        """
        Get all api keys.

        :return: All api keys.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_api_keys()
            [
                {
                    "id": 1,
                    "name": "test",
                    "userID": 1,
                    "createdDate": "2023-03-20 11:15:05",
                    "active": False,
                    "expires": null,
                    "status": "inactive"
                },
                {
                    "id": 2,
                    "name": "test2",
                    "userID": 1,
                    "createdDate": "2023-03-20 11:20:29",
                    "active": True,
                    "expires": "2023-03-30 12:20:00",
                    "status": "active"
                }
            ]
        """

        # TODO: replace with getAPIKeyList?

        r = self._get_event_data(Event.API_KEY_LIST)
        int_to_bool(r, ["active"])
        return r

    def get_api_key(self, id_: int) -> dict:
        """
        Get an api key.

        :param int id_: Id of the api key to get.
        :return: The api key.
        :rtype: dict
        :raises UptimeKumaException: If the api key does not exist.

        Example::

            >>> api.get_api_key(1)
            {
                "id": 1,
                "name": "test",
                "userID": 1,
                "createdDate": "2023-03-20 11:15:05",
                "active": False,
                "expires": null,
                "status": "inactive"
            }
        """
        api_keys = self.get_api_keys()
        for api_key in api_keys:
            if api_key["id"] == id_:
                return api_key
        raise UptimeKumaException("api key does not exist")

    def add_api_key(self, name: str, expires: str, active: bool) -> dict:
        """
        Adds a new api key.

        :param str name: Name of the api key.
        :param str expires: Expiration date of the api key. Set to ``None`` to
            disable expiration.
        :param bool active: True to activate api key.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_api_key(
            ...     name="test",
            ...     expires="2023-03-30 12:20:00",
            ...     active=True
            ... )
            {
              "msg": "Added Successfully.",
              "key": "uk1_9XPRjV7ilGj9CvWRKYiBPq9GLtQs74UzTxKfCxWY",
              "keyID": 1
            }

            >>> api.add_api_key(
            ...     name="test2",
            ...     expires=None,
            ...     active=True
            ... )
            {
              "msg": "Added Successfully.",
              "key": "uk2_jsB9H1Zmt9eEjycNFMTKgse1B0Vfvb944H4_aRqW",
              "keyID": 2
            }
        """
        data = {
            "name": name,
            "expires": expires,
            "active": 1 if active else 0
        }
        with self.wait_for_event(Event.API_KEY_LIST, new=True):
            return self._call('addAPIKey', data)

    def enable_api_key(self, id_: int) -> dict:
        """
        Enable an api key.

        :param int id_: Id of the api key to enable.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.enable_api_key(1)
            {
              "msg": "Enabled Successfully"
            }
        """
        with self.wait_for_event(Event.API_KEY_LIST, new=True):
            return self._call('enableAPIKey', id_)

    def disable_api_key(self, id_: int) -> dict:
        """
        Disable an api key.

        :param int id_: Id of the api key to disable.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.disable_api_key(1)
            {
              "msg": "Disabled Successfully."
            }
        """
        with self.wait_for_event(Event.API_KEY_LIST, new=True):
            return self._call('disableAPIKey', id_)

    def delete_api_key(self, id_: int) -> dict:
        """
        Enable an api key.

        :param int id_: Id of the api key to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_api_key(1)
            {
              "msg": "Deleted Successfully."
            }
        """
        with self.wait_for_event(Event.API_KEY_LIST):
            if id_ not in [i["id"] for i in self.get_api_keys()]:
                raise UptimeKumaException("api key does not exist")
            return self._call('deleteAPIKey', id_)
