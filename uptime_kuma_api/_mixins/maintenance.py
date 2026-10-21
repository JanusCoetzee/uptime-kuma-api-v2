from __future__ import annotations

import datetime

from ..event import Event
from ..exceptions import UptimeKumaException
from ..maintenance_strategy import MaintenanceStrategy
from ..docstrings import (
    append_docstring,
    maintenance_docstring
)
from .._helpers import (
    _check_argument_conditions,
    _check_missing_arguments,
    parse_value,
)
from ._base import MixinBase


# maintenance
def parse_maintenance_strategy(data) -> None:
    parse_value(data, "strategy", MaintenanceStrategy)


def _check_arguments_maintenance(kwargs) -> None:
    required_args = ["title", "strategy"]
    _check_missing_arguments(required_args, kwargs)

    strategy = kwargs["strategy"]
    if strategy in [
        MaintenanceStrategy.RECURRING_INTERVAL,
        MaintenanceStrategy.RECURRING_WEEKDAY,
        MaintenanceStrategy.RECURRING_DAY_OF_MONTH,
    ]:
        required_args = ["dateRange"]
        _check_missing_arguments(required_args, kwargs)

    conditions = dict(
        intervalDay=dict(
            min=1,
            max=3650,
        )
    )
    _check_argument_conditions(conditions, kwargs)


class MaintenanceMixin(MixinBase):
    def _build_maintenance_data(
            self,
            title: str,
            strategy: MaintenanceStrategy,
            active: bool = True,
            description: str = "",
            dateRange: list | None = None,
            intervalDay: int = 1,
            weekdays: list | None = None,
            daysOfMonth: list | None = None,
            timeRange: list | None = None,
            cron: str = "30 3 * * *",
            durationMinutes: int = 60,
            timezoneOption: str | None = None
    ) -> dict:
        if not dateRange:
            dateRange = [
                datetime.date.today().strftime("%Y-%m-%d 00:00:00")
            ]
        if not timeRange:
            timeRange = [
                {
                    "hours": 2,
                    "minutes": 0,
                }, {
                    "hours": 3,
                    "minutes": 0,
                }
            ]
        if not weekdays:
            weekdays = []
        if not daysOfMonth:
            daysOfMonth = []
        data = {
            "title": title,
            "active": active,
            "intervalDay": intervalDay,
            "dateRange": dateRange,
            "description": description,
            "strategy": strategy,
            "weekdays": weekdays,
            "daysOfMonth": daysOfMonth,
            "timeRange": timeRange,
            "cron": cron,
            "durationMinutes": durationMinutes,
            "timezoneOption": timezoneOption
        }
        return data

    def get_maintenances(self) -> list[dict]:
        """
        Get all maintenances.

        :return: All maintenances.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_maintenances()
            [
                {
                    "id": 1,
                    "title": "title",
                    "description": "description",
                    "strategy": <MaintenanceStrategy.SINGLE: 'single'>,
                    "intervalDay": 1,
                    "active": true,
                    "dateRange": [
                        "2022-12-27 15:39:00",
                        "2022-12-30 15:39:00"
                    ],
                    "timeRange": [
                        {
                            "hours": 0,
                            "minutes": 0
                        },
                        {
                            "hours": 0,
                            "minutes": 0
                        }
                    ],
                    "weekdays": [],
                    "daysOfMonth": [],
                    "timeslotList": [
                        {
                            "startDate": "2022-12-27 22:36:00",
                            "endDate": "2022-12-29 22:36:00"
                        }
                    ],
                    "cron": "",
                    "durationMinutes": null,
                    "timezoneOption": "Europe/Berlin",
                    "timezoneOffset": "+02:00",
                    "status": "ended"
                }
            ]
        """
        r = list(self._get_event_data(Event.MAINTENANCE_LIST).values())
        parse_maintenance_strategy(r)
        return r

    def get_maintenance(self, id_: int) -> dict:
        """
        Get a maintenance.

        :param int id_: Id of the maintenance to get.
        :return: The maintenance.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_maintenance(1)
            {
                "id": 1,
                "title": "title",
                "description": "description",
                "strategy": <MaintenanceStrategy.SINGLE: 'single'>,
                "intervalDay": 1,
                "active": true,
                "dateRange": [
                    "2022-12-27 15:39:00",
                    "2022-12-30 15:39:00"
                ],
                "timeRange": [
                    {
                        "hours": 0,
                        "minutes": 0
                    },
                    {
                        "hours": 0,
                        "minutes": 0
                    }
                ],
                "weekdays": [],
                "daysOfMonth": [],
                "timeslotList": [
                    {
                        "startDate": "2022-12-27 22:36:00",
                        "endDate": "2022-12-29 22:36:00"
                    }
                ],
                "cron": null,
                "duration": null,
                "durationMinutes": 0,
                "timezoneOption": "Europe/Berlin",
                "timezoneOffset": "+02:00",
                "status": "ended"
            }
        """
        r = self._call('getMaintenance', id_)["maintenance"]
        parse_maintenance_strategy(r)
        return r

    @append_docstring(maintenance_docstring("add"))
    def add_maintenance(self, **kwargs) -> dict:
        """
        Adds a maintenance.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example (strategy: :attr:`~.MaintenanceStrategy.MANUAL`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.MANUAL,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 00:00:00"
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[]
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }

        Example (strategy: :attr:`~.MaintenanceStrategy.SINGLE`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.SINGLE,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:36:00",
            ...         "2022-12-29 22:36:00"
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[],
            ...     timezoneOption="Europe/Berlin"
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }

        Example (strategy: :attr:`~.MaintenanceStrategy.RECURRING_INTERVAL`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.RECURRING_INTERVAL,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:37:00",
            ...         "2022-12-31 22:37:00"
            ...     ],
            ...     timeRange=[
            ...         {
            ...             "hours": 2,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         },
            ...         {
            ...             "hours": 3,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         }
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[],
            ...     timezoneOption="Europe/Berlin"
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }

        Example (strategy: :attr:`~.MaintenanceStrategy.RECURRING_WEEKDAY`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.RECURRING_WEEKDAY,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:38:00",
            ...         "2022-12-31 22:38:00"
            ...     ],
            ...     timeRange=[
            ...         {
            ...             "hours": 2,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         },
            ...         {
            ...             "hours": 3,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         }
            ...     ],
            ...     weekdays=[
            ...         1,
            ...         3,
            ...         5,
            ...         0
            ...     ],
            ...     daysOfMonth=[],
            ...     timezoneOption="Europe/Berlin"
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }

        Example (:attr:`~.MaintenanceStrategy.RECURRING_DAY_OF_MONTH`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.RECURRING_DAY_OF_MONTH,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:39:00",
            ...         "2022-12-31 22:39:00"
            ...     ],
            ...     timeRange=[
            ...         {
            ...             "hours": 2,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         },
            ...         {
            ...             "hours": 3,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         }
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[
            ...         1,
            ...         10,
            ...         20,
            ...         30,
            ...         "lastDay1"
            ...     ],
            ...     timezoneOption="Europe/Berlin"
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }

        Example (strategy: :attr:`~.MaintenanceStrategy.CRON`)::

            >>> api.add_maintenance(
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.CRON,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:39:00",
            ...         "2022-12-31 22:39:00"
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[],
            ...     cron="50 5 * * *",
            ...     durationMinutes=120,
            ...     timezoneOption="Europe/Berlin"
            ... )
            {
                "msg": "Added Successfully.",
                "maintenanceID": 1
            }
        """
        data = self._build_maintenance_data(**kwargs)
        _check_arguments_maintenance(data)
        return self._call('addMaintenance', data)

    @append_docstring(maintenance_docstring("edit"))
    def edit_maintenance(self, id_: int, **kwargs) -> dict:
        """
        Edits a maintenance.

        :param int id_: Id of the maintenance to edit.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_maintenance(1,
            ...     title="test",
            ...     description="test",
            ...     strategy=MaintenanceStrategy.RECURRING_INTERVAL,
            ...     active=True,
            ...     intervalDay=1,
            ...     dateRange=[
            ...         "2022-12-27 22:37:00",
            ...         "2022-12-31 22:37:00"
            ...     ],
            ...     timeRange=[
            ...         {
            ...             "hours": 2,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         },
            ...         {
            ...             "hours": 3,
            ...             "minutes": 0,
            ...             "seconds": 0
            ...         }
            ...     ],
            ...     weekdays=[],
            ...     daysOfMonth=[]
            ... )
            {
                "msg": "Saved.",
                "maintenanceID": 1
            }
        """
        maintenance = self.get_maintenance(id_)
        maintenance.update(kwargs)
        _check_arguments_maintenance(maintenance)
        return self._call('editMaintenance', maintenance)

    def delete_maintenance(self, id_: int) -> dict:
        """
        Deletes a maintenance.

        :param int id_: Id of the maintenance to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_maintenance(1)
            {
                "msg": "Deleted Successfully."
            }
        """
        with self.wait_for_event(Event.MAINTENANCE_LIST):
            if id_ not in [i["id"] for i in self.get_maintenances()]:
                raise UptimeKumaException("maintenance does not exist")
            return self._call('deleteMaintenance', id_)

    def pause_maintenance(self, id_: int) -> dict:
        """
        Pauses a maintenance.

        :param int id_: Id of the maintenance to pause.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.pause_maintenance(1)
            {
                "msg": "Paused Successfully."
            }
        """
        return self._call('pauseMaintenance', id_)

    def resume_maintenance(self, id_: int) -> dict:
        """
        Resumes a maintenance.

        :param int id_: Id of the maintenance to resume.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.resume_maintenance(1)
            {
                "msg": "Resume Successfully"
            }
        """
        return self._call('resumeMaintenance', id_)

    def get_monitor_maintenance(self, id_: int) -> list[dict]:
        """
        Gets all monitors of a maintenance.

        :param int id_: Id of the maintenance to get the monitors from.
        :return: All monitors of the maintenance.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_monitor_maintenance(1)
            [
                {
                    "id": 1
                },
                {
                    "id": 2
                }
            ]
        """
        return self._call('getMonitorMaintenance', id_)["monitors"]

    def add_monitor_maintenance(
            self,
            id_: int,
            monitors: list,
    ) -> dict:
        """
        Adds monitors to a maintenance.

        :param int id_: Id of the maintenance to add the monitors to.
        :param list monitors: The list of monitors to add to the maintenance.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> monitors = [
            ...     {
            ...         "id": 1
            ...     },
            ...     {
            ...         "id": 2
            ...     }
            ... ]
            >>> api.add_monitor_maintenance(1, monitors)
            {
                "msg": "Added Successfully."
            }
        """
        return self._call('addMonitorMaintenance', (id_, monitors))

    def get_status_page_maintenance(self, id_: int) -> list[dict]:
        """
        Gets all status pages of a maintenance.

        :param int id_: Id of the maintenance to get the status pages from.
        :return: All status pages of the maintenance.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_status_page_maintenance(1)
            [
                {
                    "id": 1,
                    "title": "test"
                }
            ]
        """
        return self._call('getMaintenanceStatusPage', id_)["statusPages"]

    def add_status_page_maintenance(
            self,
            id_: int,
            status_pages: list,
    ) -> dict:
        """
        Adds status pages to a maintenance.

        :param int id_: Id of the maintenance to add the monitors to.
        :param list status_pages: The list of status pages to add to the
            maintenance.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> status_pages = [
            ...     {
            ...         "id": 1
            ...     },
            ...     {
            ...         "id": 2
            ...     }
            ... ]
            >>> api.add_status_page_maintenance(1, status_pages)
            {
                "msg": "Added Successfully."
            }
        """
        return self._call('addMaintenanceStatusPage', (id_, status_pages))
