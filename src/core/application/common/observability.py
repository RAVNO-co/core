from contextlib import AbstractContextManager
from typing import Any, Protocol

from core.application.common.agent import HumanRequest


class AgentTraceContextFactory(Protocol):
    def __call__(
        self,
        request: HumanRequest,
    ) -> AbstractContextManager[Any]: ...
