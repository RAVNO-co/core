from contextlib import AbstractContextManager
from typing import Any

from langfuse import propagate_attributes

from core.application.common.agent import HumanRequest


class LangfuseTraceContextFactory:
    def __call__(
        self,
        request: HumanRequest,
    ) -> AbstractContextManager[Any]:
        return propagate_attributes(
            session_id=str(request.receipt.id), trace_name="Rozhkov"
        )
