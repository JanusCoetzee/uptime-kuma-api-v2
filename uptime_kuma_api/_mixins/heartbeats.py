from __future__ import annotations

from .. import (
    Event
)
from .._helpers import (int_to_bool, parse_monitor_status)
from ._base import MixinBase


class HeartbeatsMixin(MixinBase):
    def get_heartbeats(self) -> dict:
        """
        Get heartbeats.

        Each list holds at most the 150 newest heartbeats, ordered oldest
        first (the newest heartbeat is the last element).

        :return: The heartbeats for each monitor id.
        :rtype: dict

        Example::

            >>> api.get_heartbeats()
            {
                1: [
                    {
                        'down_count': 0,
                        'duration': 0,
                        'id': 1,
                        'important': True,
                        'monitor_id': 1,
                        'msg': '',
                        'ping': 10.5,
                        'status': <MonitorStatus.UP: 1>,
                        'time': '2023-05-01 17:22:20.289'
                    },
                    {
                        'down_count': 0,
                        'duration': 60,
                        'id': 2,
                        'important': False,
                        'monitor_id': 1,
                        'msg': '',
                        'ping': 10.7,
                        'status': <MonitorStatus.UP: 1>,
                        'time': '2023-05-01 17:23:20.349'
                    }
                ]
            }
        """
        r = self._get_event_data(Event.HEARTBEAT_LIST)
        for i in r:
            int_to_bool(r[i], ["important"])
            parse_monitor_status(r[i])
        return r

    def get_important_heartbeats(self) -> dict:
        """
        Get important heartbeats.

        Unlike :meth:`get_heartbeats`, each list is ordered newest first.

        :return: The important heartbeats for each monitor id.
        :rtype: dict

        Example::

            >>> api.get_important_heartbeats()
            {
                1: [
                    {
                        'duration': 0,
                        'important': True,
                        'monitorID': 1,
                        'msg': '',
                        'ping': 10.5,
                        'status': <MonitorStatus.UP: 1>,
                        'time': '2023-05-01 17:22:20.289'
                    }
                ]
            }
        """
        r = self._get_event_data(Event.IMPORTANT_HEARTBEAT_LIST)
        for i in r:
            int_to_bool(r[i], ["important"])
            parse_monitor_status(r[i])
        return r

    def avg_ping(self) -> dict:
        """
        Get average ping.

        :return: The average ping for each monitor id.
        :rtype: dict

        Example::

            >>> api.avg_ping()
            {
                1: 10
            }
        """
        return self._get_event_data(Event.AVG_PING)

    def cert_info(self) -> dict:
        """
        Get certificate info.

        :return: Certificate info for each monitor id for which a certificate
            can be extracted.
        :rtype: dict

        Example (long values are shortened with ``...``)::

            >>> api.cert_info()
            {
                1: {
                    'valid': True,
                    'certInfo': {
                        'subject': {
                            'CN': 'www.google.de'
                        },
                        'issuer': {
                            'C': 'US',
                            'O': 'Google Trust Services LLC',
                            'CN': 'GTS CA 1C3'
                        },
                        'subjectaltname': 'DNS:www.google.de',
                        'infoAccess': {
                            'OCSP - URI': ['http://ocsp.pki.goog/gts1c3'],
                            'CA Issuers - URI': ['http://pki.goog/repo/certs/gts1c3.der']
                        },
                        'bits': 256,
                        'pubkey': {
                            'type': 'Buffer',
                            'data': [4, 190, 87, 79, 99, 19, 100, 17, ...]
                        },
                        'asn1Curve': 'prime256v1',
                        'nistCurve': 'P-256',
                        'valid_from': 'Apr  3 08:24:23 2023 GMT',
                        'valid_to': 'Jun 26 08:24:22 2023 GMT',
                        'fingerprint': '45:B2:16:8F:B0:00:25:31...',
                        'fingerprint256': '5E:77:02:E0:DE:28:33:5E...',
                        'fingerprint512': '35:D5:F8:24:BD:20:06:B1...',
                        'ext_key_usage': ['1.3.6.1.5.5.7.3.1'],
                        'serialNumber': '8628F43381B42BA50A686F0ACB522E40',
                        'raw': {
                            'type': 'Buffer',
                            'data': [48, 130, 4, 136, 48, 130, 3, 112, ...]
                        },
                        'issuerCertificate': {
                            'subject': {
                                'C': 'US',
                                'O': 'Google Trust Services LLC',
                                'CN': 'GTS CA 1C3'
                            },
                            'issuer': {
                                'C': 'US',
                                'O': 'Google Trust Services LLC',
                                'CN': 'GTS Root R1'
                            },
                            'infoAccess': {
                                'OCSP - URI': ['http://ocsp.pki.goog/gtsr1'],
                                'CA Issuers - URI': ['http://pki.goog/repo/certs/gtsr1.der']
                            },
                            'modulus': 'F588DFE7628...',
                            'bits': 2048,
                            'exponent': '0x10001',
                            'pubkey': {
                                'type': 'Buffer',
                                'data': [48, 130, 1, 34, 48, 13, 6, 9, ...]
                            },
                            'valid_from': 'Aug 13 00:00:42 2020 GMT',
                            'valid_to': 'Sep 30 00:00:42 2027 GMT',
                            'fingerprint': '1E:7E:F6:47:CB:A1:50:28...',
                            'fingerprint256': '23:EC:B0:3E:EC:17:33:8C...',
                            'fingerprint512': '43:7B:9E:11:1E:EB:78:01...',
                            'ext_key_usage': [
                                '1.3.6.1.5.5.7.3.1',
                                '1.3.6.1.5.5.7.3.2'
                            ],
                            'serialNumber': '0203BC53596B34C718F5015066',
                            'raw': {
                                'type': 'Buffer',
                                'data': [48, 130, 5, 150, 48, 130, 3, 126, ...]
                            },
                            'issuerCertificate': {
                                'subject': {
                                    'C': 'US',
                                    'O': 'Google Trust Services LLC',
                                    'CN': 'GTS Root R1'
                                },
                                'issuer': {
                                    'C': 'BE',
                                    'O': 'GlobalSign nv-sa',
                                    'OU': 'Root CA',
                                    'CN': 'GlobalSign Root CA'
                                },
                                'infoAccess': {
                                    'OCSP - URI': ['http://ocsp.pki.goog/gsr1'],
                                    'CA Issuers - URI': ['http://pki.goog/gsr1/gsr1.crt']
                                },
                                'modulus': 'B611028B1EE...',
                                'bits': 4096,
                                'exponent': '0x10001',
                                'pubkey': {
                                    'type': 'Buffer',
                                    'data': [48, 130, 2, 34, 48, 13, 6, 9, ...]
                                },
                                'valid_from': 'Jun 19 00:00:42 2020 GMT',
                                'valid_to': 'Jan 28 00:00:42 2028 GMT',
                                'fingerprint': '08:74:54:87:E8:91:C1:9E...',
                                'fingerprint256': '3E:E0:27:8D:F7:1F:A3:C1...',
                                'fingerprint512': '7C:88:3C:25:8B:8D:E7:34...',
                                'serialNumber': '77BD0D6CDB3...',
                                'raw': {
                                    'type': 'Buffer',
                                    'data': [48, 130, 5, 98, ...]
                                },
                                'issuerCertificate': {
                                    'subject': {
                                        'C': 'BE',
                                        'O': 'GlobalSign nv-sa',
                                        'OU': 'Root CA',
                                        'CN': 'GlobalSign Root CA'
                                    },
                                    'issuer': {
                                        'C': 'BE',
                                        'O': 'GlobalSign nv-sa',
                                        'OU': 'Root CA',
                                        'CN': 'GlobalSign Root CA'
                                    },
                                    'modulus': 'DA0EE6998DC...',
                                    'bits': 2048,
                                    'exponent': '0x10001',
                                    'pubkey': {
                                        'type': 'Buffer',
                                        'data': [48, 130, 1, 34, ...]
                                    },
                                    'valid_from': 'Sep  1 12:00:00 1998 GMT',
                                    'valid_to': 'Jan 28 12:00:00 2028 GMT',
                                    'fingerprint': 'B1:BC:96:8B...',
                                    'fingerprint256': 'EB:D4:10:40...',
                                    'fingerprint512': '54:BA:00:4D...',
                                    'serialNumber': '040000000001154B5AC394',
                                    'raw': {
                                        'type': 'Buffer',
                                        'data': [48, 130, 3, 117, ...]
                                    },
                                    'issuerCertificate': None,
                                    'validTo': '2028-01-28T12:00:00.000Z',
                                    'daysRemaining': 1733
                                },
                                'validTo': '2028-01-28T00:00:42.000Z',
                                'daysRemaining': 1732
                            },
                            'validTo': '2027-09-30T00:00:42.000Z',
                            'daysRemaining': 1612
                        },
                        'validTo': '2023-06-26T08:24:22.000Z',
                        'validFor': ['www.google.de'],
                        'daysRemaining': 56
                    }
                }
            }
        """
        return self._get_event_data(Event.CERT_INFO)

    def uptime(self) -> dict:
        """
        Get monitor uptime.

        :return: Monitor uptime.
        :rtype: dict

        Example::

            >>> api.uptime()
            {
                1: {
                    24: 1,
                    720: 1
                }
            }
        """
        return self._get_event_data(Event.UPTIME)

    def info(self) -> dict:
        """
        Get server info.

        :return: Server info.
        :rtype: dict

        Example::

            >>> api.info()
            {
                'isContainer': True,
                'latestVersion': '1.23.1',
                'primaryBaseURL': '',
                'serverTimezone': 'Europe/Berlin',
                'serverTimezoneOffset': '+02:00',
                'version': '1.23.1'
            }
        """
        r = self._get_event_data(Event.INFO)
        return r

    def clear_events(self, monitor_id: int) -> dict:
        """
        Clear monitor events.

        :param int monitor_id: Id of the monitor to clear events.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.clear_events(1)
            {}
        """
        return self._call('clearEvents', monitor_id)

    def clear_heartbeats(self, monitor_id: int) -> dict:
        """
        Clear monitor heartbeats.

        :param int monitor_id: Id of the monitor to clear heartbeats.
        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.clear_heartbeats(1)
            {}
        """
        return self._call('clearHeartbeats', monitor_id)

    def clear_statistics(self) -> dict:
        """
        Clear statistics.

        :return: The server response.
        :rtype: dict
        :raises UptimeKumaException: If the server returns an error.

        Example::

            >>> api.clear_statistics()
            {}
        """
        return self._call('clearStatistics')
