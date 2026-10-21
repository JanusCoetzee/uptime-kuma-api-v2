# uptime-kuma-api-v2
[![Upload Python Package](https://github.com/JanusCoetzee/uptime-kuma-api-v2/actions/workflows/python-publish.yml/badge.svg)](https://github.com/JanusCoetzee/uptime-kuma-api-v2/actions/workflows/python-publish.yml)
A wrapper for the Uptime Kuma Socket.IO API
---
uptime-kuma-api-v2 is a Python wrapper for the [Uptime Kuma](https://github.com/louislam/uptime-kuma) Socket.IO API.

Acknowledgements
---
This project is a fork of [uptime-kuma-api](https://github.com/lucasheld/uptime-kuma-api) by [Lucas Held](https://github.com/lucasheld) (MIT licensed), via the [exaland/uptime-kuma-api-v2](https://github.com/exaland/uptime-kuma-api-v2) fork that added Uptime Kuma 2.x support. Thank you to both authors. It is now maintained independently and is diverging significantly from upstream, so expect API changes. Both original copyright notices are kept in [LICENSE](LICENSE).


Python version 3.12+ is required.

Supported Uptime Kuma versions:

| Uptime Kuma     | uptime-kuma-api-v2 |
|-----------------|-----------------|
| 2.0.0-beta.2     | 1.0.0 - 1.0.3   |
| 2.5.6            | 2.0.0 (tested in CI) |

The library has its own version, independent of the Uptime Kuma version: from 2.0.0 it follows [semantic versioning](https://semver.org/), so a breaking change to the Python API bumps the major version. Uptime Kuma 1.x is not supported (the 1.x code paths were removed in #33). Only 2.5.6 is tested in CI; other 2.x versions are expected to work but are not tested.


Installation
---
uptime-kuma-api-v2 is available on the [Python Package Index (PyPI)](https://pypi.org/project/uptime-kuma-api-v2/).

You can install it using pip:

```
pip install uptime-kuma-api-v2
```

> **Import name conflict:** the import package is still `uptime_kuma_api`, the same as the original `uptime-kuma-api` distribution. If both are installed they overwrite each other's files, so install only one of them.

Documentation
---
The API Reference is available on [Read the Docs](https://uptime-kuma-api-v2.readthedocs.io).

Example
---
Once you have installed the python package, you can use it to communicate with an Uptime Kuma instance.

To do so, import `UptimeKumaApi` from the library and specify the Uptime Kuma server url (e.g. 'http://127.0.0.1:3001'), username and password to initialize the connection.

```python
>>> from uptime_kuma_api import UptimeKumaApi, MonitorType
>>> api = UptimeKumaApi('INSERT_URL')
>>> api.login('INSERT_USERNAME', 'INSERT_PASSWORD')
```

Now you can call one of the existing methods of the instance. For example create a new monitor:

```python
>>> result = api.add_monitor(type=MonitorType.HTTP, name="Google", url="https://google.com")
>>> print(result)
{'msg': 'Added Successfully.', 'monitorId': 1}
```

At the end, the connection to the API must be disconnected so that the program does not block.

```python
>>> api.disconnect()
```

With a context manager, the disconnect method is called automatically:

```python
from uptime_kuma_api import UptimeKumaApi

with UptimeKumaApi('INSERT_URL') as api:
    api.login('INSERT_USERNAME', 'INSERT_PASSWORD')
    api.add_monitor(
        type=MonitorType.HTTP,
        name="Google",
        url="https://google.com"
    )
```
