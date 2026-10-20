"""What the mixins use from ``UptimeKumaApi``, declared for type checkers.

Each mixin calls ``self._call`` and friends, which only exist on the
assembled ``UptimeKumaApi``. At runtime ``MixinBase`` is an empty class; the
real members are defined in ``api.py`` (keep the signatures in sync, mypy
checks the overrides).
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from contextlib import AbstractContextManager
    from typing import Any

    from ..event import Event

    class MixinBase:
        url: str
        timeout: float
        headers: dict | None
        ssl_verify: bool
        wait_events: float
        _lock: Any
        _event_data: dict

        @property
        def version(self) -> str: ...

        def _call(self, event, data=None) -> Any: ...

        def _get_event_data(self, event) -> Any: ...

        def wait_for_event(
            self, event: Event, new: bool = False
        ) -> AbstractContextManager[None]: ...

        def get_monitors(self) -> list[dict]: ...

        def get_heartbeats(self) -> dict: ...
else:
    class MixinBase:
        pass
