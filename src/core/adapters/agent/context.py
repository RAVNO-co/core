from typing import Protocol, TypedDict

from core.application.common.agent import HumanRequest
from core.domain.value_objects import UserID


class ReceiptModificationContext(TypedDict):
    current_user_id: UserID


class ContextFactory(Protocol):
    def __call__(
        self, request: HumanRequest
    ) -> ReceiptModificationContext: ...


def create_context(request: HumanRequest) -> ReceiptModificationContext:
    return {"current_user_id": request.user_id}
