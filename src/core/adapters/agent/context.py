from typing import Protocol, TypedDict

from core.domain.value_objects import UserID


class ReceiptModificationContext(TypedDict):
    current_user_id: UserID


class ContextFactory(Protocol):
    def __call__(
        self, current_user_id: UserID
    ) -> ReceiptModificationContext: ...


def create_context(current_user_id: UserID) -> ReceiptModificationContext:
    return {"current_user_id": current_user_id}
