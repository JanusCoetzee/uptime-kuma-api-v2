from __future__ import annotations

from packaging.version import parse as parse_version

from .. import (
    AuthMethod,
    Event,
    MonitorStatus,
    MonitorType,
    UptimeKumaException
)
from ..docstrings import (
    append_docstring,
    monitor_docstring
)
from .._helpers import (int_to_bool, parse_monitor_status)
from .._monitor_args import (
    _check_arguments_monitor,
    _convert_monitor_input,
    _convert_monitor_return,
    parse_auth_method,
    parse_monitor_type,
)


class MonitorsMixin:
    def _build_monitor_data(
            self,
            type: MonitorType,
            name: str,
            parent: int = None,
            description: str = None,
            conditions: list = None,
            interval: int = 60,
            retryInterval: int = 60,
            resendInterval: int = 0,
            maxretries: int = 1,
            upsideDown: bool = False,
            notificationIDList: list = None,
            httpBodyEncoding: str = "json",

            # HTTP, KEYWORD, JSON_QUERY, REAL_BROWSER
            url: str = None,

            # HTTP, KEYWORD, GRPC_KEYWORD
            maxredirects: int = 10,
            accepted_statuscodes: list[str] = None,

            # HTTP, KEYWORD, JSON_QUERY
            expiryNotification: bool = False,
            ignoreTls: bool = False,
            proxyId: int = None,
            method: str = "GET",
            body: str = None,
            headers: str = None,
            authMethod: AuthMethod = AuthMethod.NONE,
            tlsCert: str = None,
            tlsKey: str = None,
            tlsCa: str = None,
            basic_auth_user: str = None,
            basic_auth_pass: str = None,
            authDomain: str = None,
            authWorkstation: str = None,
            oauth_auth_method: str = "client_secret_basic",
            oauth_token_url: str = None,
            oauth_client_id: str = None,
            oauth_client_secret: str = None,
            oauth_scopes: str = None,
            timeout: int = 48,

            # KEYWORD
            keyword: str = None,
            invertKeyword: bool = False,

            # GRPC_KEYWORD
            grpcUrl: str = None,
            grpcEnableTls: bool = False,
            grpcServiceName: str = None,
            grpcMethod: str = None,
            grpcProtobuf: str = None,
            grpcBody: str = None,
            grpcMetadata: str = None,

            # PORT, PING, DNS, STEAM, MQTT, RADIUS, TAILSCALE_PING
            hostname: str = None,

            # PING
            packetSize: int = 56,

            # PORT, DNS, STEAM, MQTT, RADIUS
            port: int = None,

            # DNS
            dns_resolve_server: str = "1.1.1.1",
            dns_resolve_type: str = "A",

            # MQTT
            mqttUsername: str = "",
            mqttPassword: str = "",
            mqttTopic: str = "",
            mqttSuccessMessage: str = "",

            # SQLSERVER, POSTGRES, MYSQL, MONGODB, REDIS
            databaseConnectionString: str = None,

            # SQLSERVER, POSTGRES, MYSQL
            databaseQuery: str = None,

            # DOCKER
            docker_container: str = "",
            docker_host: int = None,

            # RADIUS
            radiusUsername: str = None,
            radiusPassword: str = None,
            radiusSecret: str = None,
            radiusCalledStationId: str = None,
            radiusCallingStationId: str = None,

            # GAMEDIG
            game: str = None,
            gamedigGivenPortOnly: bool = True,

            # JSON_QUERY
            jsonPath: str = None,
            expectedValue: str = None,

            # KAFKA_PRODUCER
            kafkaProducerBrokers: list[str] = None,
            kafkaProducerTopic: str = None,
            kafkaProducerMessage: str = None,
            kafkaProducerSsl: bool = False,
            kafkaProducerAllowAutoTopicCreation: bool = False,
            kafkaProducerSaslOptions: dict = None,
    ) -> dict:
        if accepted_statuscodes is None:
            accepted_statuscodes = ["200-299"]

        if notificationIDList is None:
            notificationIDList = {}

        data = {
            "type": type,
            "name": name,
            "interval": interval,
            "retryInterval": retryInterval,
            "maxretries": maxretries,
            "notificationIDList": notificationIDList,
            "upsideDown": upsideDown,
            "resendInterval": resendInterval,
            "description": description,
            "conditions": conditions,
            "httpBodyEncoding": httpBodyEncoding,
        }

        if parse_version(self.version) >= parse_version("1.22"):
            data.update({
                "parent": parent,
            })

        if type in [MonitorType.KEYWORD, MonitorType.GRPC_KEYWORD]:
            data.update({
                "keyword": keyword,
            })
            if parse_version(self.version) >= parse_version("1.23"):
                data.update({
                    "invertKeyword": invertKeyword,
                })

        # HTTP, KEYWORD, JSON_QUERY, REAL_BROWSER
        data.update({
            "url": url,
        })

        # HTTP, KEYWORD, GRPC_KEYWORD
        data.update({
            "maxredirects": maxredirects,
            "accepted_statuscodes": accepted_statuscodes,
        })

        data.update({
            "expiryNotification": expiryNotification,
            "ignoreTls": ignoreTls,
            "proxyId": proxyId,
            "method": method,
            "body": body,
            "headers": headers,
            "authMethod": authMethod,
        })

        if parse_version(self.version) >= parse_version("1.23"):
            data.update({
                "timeout": timeout,
            })

        if authMethod in [AuthMethod.HTTP_BASIC, AuthMethod.NTLM]:
            data.update({
                "basic_auth_user": basic_auth_user,
                "basic_auth_pass": basic_auth_pass,
            })

        if authMethod == AuthMethod.NTLM:
            data.update({
                "authDomain": authDomain,
                "authWorkstation": authWorkstation,
            })

        if authMethod == AuthMethod.MTLS:
            data.update({
                "tlsCert": tlsCert,
                "tlsKey": tlsKey,
                "tlsCa": tlsCa,
            })

        if authMethod == AuthMethod.OAUTH2_CC:
            data.update({
                "oauth_auth_method": oauth_auth_method,
                "oauth_token_url": oauth_token_url,
                "oauth_client_id": oauth_client_id,
                "oauth_client_secret": oauth_client_secret,
                "oauth_scopes": oauth_scopes,
            })

        # GRPC_KEYWORD
        if type == MonitorType.GRPC_KEYWORD:
            data.update({
                "grpcUrl": grpcUrl,
                "grpcEnableTls": grpcEnableTls,
                "grpcServiceName": grpcServiceName,
                "grpcMethod": grpcMethod,
                "grpcProtobuf": grpcProtobuf,
                "grpcBody": grpcBody,
                "grpcMetadata": grpcMetadata,
            })

        # PORT, PING, DNS, STEAM, MQTT, RADIUS, TAILSCALE_PING
        data.update({
            "hostname": hostname,
        })

        # PING
        data.update({
            "packetSize": packetSize,
        })

        # PORT, DNS, STEAM, MQTT, RADIUS
        if not port:
            if type == MonitorType.DNS:
                port = 53
            elif type == MonitorType.RADIUS:
                port = 1812
        data.update({
            "port": port,
        })

        # DNS
        data.update({
            "dns_resolve_server": dns_resolve_server,
            "dns_resolve_type": dns_resolve_type,
        })

        # MQTT
        data.update({
            "mqttUsername": mqttUsername,
            "mqttPassword": mqttPassword,
            "mqttTopic": mqttTopic,
            "mqttSuccessMessage": mqttSuccessMessage,
        })

        # SQLSERVER, POSTGRES, MYSQL, MONGODB, REDIS
        data.update({
            "databaseConnectionString": databaseConnectionString
        })

        # SQLSERVER, POSTGRES, MYSQL
        if type in [MonitorType.SQLSERVER, MonitorType.POSTGRES, MonitorType.MYSQL]:
            data.update({
                "databaseQuery": databaseQuery,
            })

        # DOCKER
        if type == MonitorType.DOCKER:
            data.update({
                "docker_container": docker_container,
                "docker_host": docker_host,
            })

        # RADIUS
        if type == MonitorType.RADIUS:
            data.update({
                "radiusUsername": radiusUsername,
                "radiusPassword": radiusPassword,
                "radiusSecret": radiusSecret,
                "radiusCalledStationId": radiusCalledStationId,
                "radiusCallingStationId": radiusCallingStationId,
            })

        # GAMEDIG
        if type == MonitorType.GAMEDIG:
            data.update({
                "game": game,
            })
            if parse_version(self.version) >= parse_version("1.23"):
                data.update({
                    "gamedigGivenPortOnly": gamedigGivenPortOnly,
                })

        # JSON_QUERY
        if type == MonitorType.JSON_QUERY:
            data.update({
                "jsonPath": jsonPath,
                "expectedValue": expectedValue,
            })

        # KAFKA_PRODUCER
        if type == MonitorType.KAFKA_PRODUCER:
            if kafkaProducerBrokers is None:
                kafkaProducerBrokers = []
            if not kafkaProducerSaslOptions:
                kafkaProducerSaslOptions = {
                    "mechanism": "None",
                }
            data.update({
                "kafkaProducerBrokers": kafkaProducerBrokers,
                "kafkaProducerTopic": kafkaProducerTopic,
                "kafkaProducerMessage": kafkaProducerMessage,
                "kafkaProducerSsl": kafkaProducerSsl,
                "kafkaProducerAllowAutoTopicCreation": kafkaProducerAllowAutoTopicCreation,
                "kafkaProducerSaslOptions": kafkaProducerSaslOptions,
            })
        return data

    def get_monitors(self) -> list[dict]:
        """
        Get all monitors.

        :return: A list of monitors.
        :rtype: list

        Example::

            >>> api.get_monitors()
            [
                {
                    'accepted_statuscodes': ['200-299'],
                    'active': True,
                    'authDomain': None,
                    'authMethod': <AuthMethod.NONE: ''>,
                    'authWorkstation': None,
                    'basic_auth_pass': None,
                    'basic_auth_user': None,
                    'body': None,
                    'childrenIDs': [],
                    'databaseConnectionString': None,
                    'databaseQuery': None,
                    'description': None,
                    'dns_last_result': None,
                    'dns_resolve_server': '1.1.1.1',
                    'dns_resolve_type': 'A',
                    'docker_container': None,
                    'docker_host': None,
                    'expiryNotification': False,
                    'forceInactive': False,
                    'game': None,
                    'grpcBody': None,
                    'grpcEnableTls': False,
                    'grpcMetadata': None,
                    'grpcMethod': None,
                    'grpcProtobuf': None,
                    'grpcServiceName': None,
                    'grpcUrl': None,
                    'headers': None,
                    'hostname': None,
                    'httpBodyEncoding': 'json',
                    'id': 1,
                    'ignoreTls': False,
                    'includeSensitiveData': True,
                    'interval': 60,
                    'keyword': None,
                    'maintenance': False,
                    'maxredirects': 10,
                    'maxretries': 0,
                    'method': 'GET',
                    'mqttPassword': None,
                    'mqttSuccessMessage': None,
                    'mqttTopic': None,
                    'mqttUsername': None,
                    'name': 'monitor 1',
                    'notificationIDList': [1, 2],
                    'packetSize': 56,
                    'parent': None,
                    'pathName': 'monitor 1',
                    'port': None,
                    'proxyId': None,
                    'pushToken': None,
                    'radiusCalledStationId': None,
                    'radiusCallingStationId': None,
                    'radiusPassword': None,
                    'radiusSecret': None,
                    'radiusUsername': None,
                    'resendInterval': 0,
                    'retryInterval': 60,
                    'tags': [],
                    'tlsCa': None,
                    'tlsCert': None,
                    'tlsKey': None,
                    'type': <MonitorType.HTTP: 'http'>,
                    'upsideDown': False,
                    'url': 'http://127.0.0.1',
                    'weight': 2000
                }
            ]
        """

        # TODO: replace with getMonitorList?

        r = list(self._get_event_data(Event.MONITOR_LIST).values())
        for monitor in r:
            _convert_monitor_return(monitor)
        int_to_bool(r, ["active"])
        parse_monitor_type(r)
        parse_auth_method(r)
        return r

    def get_monitor(self, id_: int) -> dict:
        """
        Get a monitor.

        :param int id_: The monitor id.
        :return: The monitor.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_monitor(1)
            {
                'accepted_statuscodes': ['200-299'],
                'active': True,
                'authDomain': None,
                'authMethod': <AuthMethod.NONE: ''>,
                'authWorkstation': None,
                'basic_auth_pass': None,
                'basic_auth_user': None,
                'body': None,
                'childrenIDs': [],
                'databaseConnectionString': None,
                'databaseQuery': None,
                'description': None,
                'dns_last_result': None,
                'dns_resolve_server': '1.1.1.1',
                'dns_resolve_type': 'A',
                'docker_container': None,
                'docker_host': None,
                'expectedValue': None,
                'expiryNotification': False,
                'forceInactive': False,
                'game': None,
                'gamedigGivenPortOnly': True,
                'grpcBody': None,
                'grpcEnableTls': False,
                'grpcMetadata': None,
                'grpcMethod': None,
                'grpcProtobuf': None,
                'grpcServiceName': None,
                'grpcUrl': None,
                'headers': None,
                'hostname': None,
                'httpBodyEncoding': 'json',
                'id': 1,
                'ignoreTls': False,
                'includeSensitiveData': True,
                'interval': 60,
                'invertKeyword': False,
                'jsonPath': None,
                'kafkaProducerAllowAutoTopicCreation': False,
                'kafkaProducerBrokers': None,
                'kafkaProducerMessage': None,
                'kafkaProducerSaslOptions': None,
                'kafkaProducerSsl': False,
                'kafkaProducerTopic': None,
                'keyword': None,
                'maintenance': False,
                'maxredirects': 10,
                'maxretries': 0,
                'method': 'GET',
                'mqttPassword': '',
                'mqttSuccessMessage': '',
                'mqttTopic': '',
                'mqttUsername': '',
                'name': 'monitor 1',
                'notificationIDList': [1, 2],
                'oauth_auth_method': None,
                'oauth_client_id': None,
                'oauth_client_secret': None,
                'oauth_scopes': None,
                'oauth_token_url': None,
                'packetSize': 56,
                'parent': None,
                'pathName': 'monitor 1',
                'port': None,
                'proxyId': None,
                'pushToken': None,
                'radiusCalledStationId': None,
                'radiusCallingStationId': None,
                'radiusPassword': None,
                'radiusSecret': None,
                'radiusUsername': None,
                'resendInterval': 0,
                'retryInterval': 60,
                'screenshot': None,
                'tags': [],
                'timeout': 48,
                'tlsCa': None,
                'tlsCert': None,
                'tlsKey': None,
                'type': <MonitorType.HTTP: 'http'>,
                'upsideDown': False,
                'url': 'http://127.0.0.1',
                'weight': 2000
            }
        """
        r = self._call('getMonitor', id_)["monitor"]
        _convert_monitor_return(r)
        int_to_bool(r, ["active"])
        parse_monitor_type(r)
        parse_auth_method(r)
        return r

    def pause_monitor(self, id_: int) -> dict:
        """
        Pauses a monitor.

        :param int id_: The monitor id.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.pause_monitor(1)
            {
                'msg': 'Paused Successfully.'
            }
        """
        return self._call('pauseMonitor', id_)

    def resume_monitor(self, id_: int) -> dict:
        """
        Resumes a monitor.

        :param int id_: The monitor id.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.resume_monitor(1)
            {
                'msg': 'Resumed Successfully.'
            }
        """
        return self._call('resumeMonitor', id_)

    def delete_monitor(self, id_: int) -> dict:
        """
        Deletes a monitor.

        :param int id_: The monitor id.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.delete_monitor(1)
            {
                'msg': 'Deleted Successfully.'
            }
        """
        with self.wait_for_event(Event.MONITOR_LIST):
            if id_ not in [i["id"] for i in self.get_monitors()]:
                raise UptimeKumaException("monitor does not exist")
            return self._call('deleteMonitor', id_)

    def get_monitor_beats(self, id_: int, hours: int) -> list[dict]:
        """
        Get monitor beats for a specific monitor in a time range.

        :param int id_: The monitor id.
        :param int hours: Period time in hours from now.
        :return: The server response.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_monitor_beats(1, 6)
            [
                {
                    'down_count': 0,
                    'duration': 0,
                    'id': 25,
                    'important': True,
                    'monitor_id': 1,
                    'msg': '200 - OK',
                    'ping': 201,
                    'status': <MonitorStatus.UP: 1>,
                    'time': '2022-12-15 12:38:42.661'
                },
                {
                    'down_count': 0,
                    'duration': 60,
                    'id': 26,
                    'important': False,
                    'monitor_id': 1,
                    'msg': '200 - OK',
                    'ping': 193,
                    'status': <MonitorStatus.UP: 1>,
                    'time': '2022-12-15 12:39:42.878'
                },
                ...
            ]
        """
        r = self._call('getMonitorBeats', (id_, hours))["data"]
        int_to_bool(r, ["important"])
        parse_monitor_status(r)
        return r

    def get_game_list(self) -> list[dict]:
        """
        Get a list of games that are supported by the GameDig monitor type.

        :return: The server response.
        :rtype: list
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.get_game_list()
            [
                {
                    'extra': {},
                    'keys': ['7d2d'],
                    'options': {
                        'port': 26900,
                        'port_query_offset': 1,
                        'protocol': 'valve'
                    },
                    'pretty': '7 Days to Die (2013)'
                },
                {
                    'extra': {},
                    'keys': ['arma2'],
                    'options': {
                        'port': 2302,
                        'port_query_offset': 1,
                        'protocol': 'valve'
                    },
                    'pretty': 'ARMA 2 (2009)'
                },
                ...
            ]
        """
        r = self._call('getGameList')
        return r.get("gameList")

    def test_chrome(self, executable) -> dict:
        """
        Test if the chrome executable is valid and return the version.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.test_chrome("/usr/bin/chromium")
            {
                'msg': 'Found Chromium/Chrome. Version: 90.0.4430.212'
            }
        """
        return self._call('testChrome', executable)

    @append_docstring(monitor_docstring("add"))
    def add_monitor(self, **kwargs) -> dict:
        """
        Adds a new monitor.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.add_monitor(
            ...     type=MonitorType.HTTP,
            ...     name="Google",
            ...     url="https://google.com"
            ... )
            {
                'msg': 'Added Successfully.',
                'monitorID': 1
            }
        """
        data = self._build_monitor_data(**kwargs)
        _convert_monitor_input(data)
        _check_arguments_monitor(data)
        with self.wait_for_event(Event.MONITOR_LIST, new=True):
            return self._call('add', data)

    @append_docstring(monitor_docstring("edit"))
    def edit_monitor(self, id_: int, **kwargs) -> dict:
        """
        Edits an existing monitor.

        :param int id_: The monitor id.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.edit_monitor(1,
            ...     interval=20
            ... )
            {
                'monitorID': 1,
                'msg': 'Saved.'
            }
        """
        data = self.get_monitor(id_)
        data.update(kwargs)
        _convert_monitor_input(data)
        _check_arguments_monitor(data)
        with self.wait_for_event(Event.MONITOR_LIST, new=True):
            return self._call('editMonitor', data)

    def get_monitor_status(self, monitor_id: int) -> MonitorStatus:
        """
        Get the monitor status.

        The status is taken from the last (newest) element of the monitor's
        heartbeat list, see :meth:`get_heartbeats`.

        :param int monitor_id: Id of the monitor.
        :return: The monitor status.
        :rtype: MonitorStatus
        :raises UptimeKumaException: If the monitor does not exist.

        Example::

            >>> api.get_monitor_status(1)
            <MonitorStatus.PENDING: 2>
        """
        heartbeats = self.get_heartbeats()
        for heartbeat_monitor_id in heartbeats:
            if heartbeat_monitor_id == monitor_id:
                status = heartbeats[heartbeat_monitor_id][-1]["status"]
                return MonitorStatus(status)
        raise UptimeKumaException("monitor does not exist")
