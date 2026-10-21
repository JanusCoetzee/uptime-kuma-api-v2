from __future__ import annotations

from ..docker_type import DockerType
from ..event import Event
from ..exceptions import UptimeKumaException
from ..docstrings import (
    append_docstring,
    docker_host_docstring
)
from .._helpers import _check_edit_arguments, parse_value
from ._base import MixinBase


# docker host
def parse_docker_type(data) -> None:
    parse_value(data, "dockerType", DockerType)


def _convert_docker_host_input(kwargs) -> None:
    if not kwargs["dockerDaemon"]:
        if kwargs["dockerType"] == DockerType.SOCKET:
            kwargs["dockerDaemon"] = "/var/run/docker.sock"
        elif kwargs["dockerType"] == DockerType.TCP:
            kwargs["dockerDaemon"] = "tcp://localhost:2375"


def _build_docker_host_data(
    name: str,
    dockerType: DockerType,
    dockerDaemon: str | None = None
) -> dict:
    data = {
        "name": name,
        "dockerType": dockerType,
        "dockerDaemon": dockerDaemon
    }
    return data


class DockerHostsMixin(MixinBase):
    def get_docker_hosts(self) -> list[dict]:
        """
        Get all docker hosts.

        :return: All docker hosts.
        :rtype: list

        Example::

            >>> api.get_docker_hosts()
            [
                {
                    'dockerDaemon': '/var/run/docker.sock',
                    'dockerType': <DockerType.SOCKET: 'socket'>,
                    'id': 1,
                    'name': 'name 1',
                    'userID': 1
                }
            ]
        """
        r = self._get_event_data(Event.DOCKER_HOST_LIST)
        parse_docker_type(r)
        return r

    def get_docker_host(self, id_: int) -> dict:
        """
        Get a docker host.

        :param int id_: Id of the docker host to get.
        :return: The docker host.
        :rtype: dict
        :raises UptimeKumaException: If the docker host does not exist.

        Example::

            >>> api.get_docker_host(1)
            {
                'dockerDaemon': '/var/run/docker.sock',
                'dockerType': 'socket',
                'id': 1,
                'name': 'name 1',
                'userID': 1
            }
        """
        docker_hosts = self.get_docker_hosts()
        for docker_host in docker_hosts:
            if docker_host["id"] == id_:
                return docker_host
        raise UptimeKumaException("docker host does not exist")

    @append_docstring(docker_host_docstring("test"), validated=False)
    def test_docker_host(self, **kwargs) -> dict:
        """
        Test a docker host.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.test_docker_host(
            ...     name="name 1",
            ...     dockerType=DockerType.SOCKET,
            ...     dockerDaemon="/var/run/docker.sock"
            ... )
            {
                'msg': 'Connected Successfully. Amount of containers: 10'
            }
        """
        data = _build_docker_host_data(**kwargs)
        return self._call('testDockerHost', data)

    @append_docstring(docker_host_docstring("add"), validated=False)
    def add_docker_host(self, **kwargs) -> dict:
        """
        Add a docker host.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_docker_host(
            ...     name="name 1",
            ...     dockerType=DockerType.SOCKET,
            ...     dockerDaemon="/var/run/docker.sock"
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        data = _build_docker_host_data(**kwargs)
        _convert_docker_host_input(data)
        with self.wait_for_event(Event.DOCKER_HOST_LIST, new=True):
            return self._call('addDockerHost', (data, None))

    @append_docstring(docker_host_docstring("edit"), validated=False)
    def edit_docker_host(self, id_: int, **kwargs) -> dict:
        """
        Edit a docker host.

        :param int id_: Id of the docker host to edit.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_docker_host(1,
            ...     name="name 2"
            ... )
            {
                'id': 1,
                'msg': 'Saved'
            }
        """
        data = self.get_docker_host(id_)
        _check_edit_arguments(
            "edit_docker_host", kwargs, _build_docker_host_data, data)
        data.update(kwargs)
        _convert_docker_host_input(data)
        with self.wait_for_event(Event.DOCKER_HOST_LIST, new=True):
            return self._call('addDockerHost', (data, id_))

    def delete_docker_host(self, id_: int) -> dict:
        """
        Delete a docker host.

        :param int id_: Id of the docker host to delete.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_docker_host(1)
            {
                'msg': 'Deleted'
            }
        """
        with self.wait_for_event(Event.DOCKER_HOST_LIST):
            if id_ not in [i["id"] for i in self.get_docker_hosts()]:
                raise UptimeKumaException("docker host does not exist")
            return self._call('deleteDockerHost', id_)
