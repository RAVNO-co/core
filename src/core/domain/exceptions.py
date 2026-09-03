from decimal import Decimal
from typing import Annotated, Literal

from annotated_types import Gt

from core.domain.value_objects.types import (
    AssignmentKind,
    LineItemID,
    UserID,
)

Amount = Annotated[Decimal, Gt(0)]


class DomainError(Exception): ...


class OverAssignmentError(DomainError):
    kind: AssignmentKind
    user_id: UserID
    current: Amount | Literal[0]
    added: Amount
    limit: Amount

    def __init__(
        self,
        kind: AssignmentKind,
        user_id: UserID,
        current: Amount | Literal[0],
        added: Amount,
        limit: Amount,
    ) -> None:
        self.kind = kind
        self.user_id = user_id
        self.added = added
        self.limit = limit
        self.current = current
        super().__init__()


class NegativeAssignmentError(DomainError):
    kind: AssignmentKind
    user_id: UserID
    current: Amount | Literal[0]
    removed: Amount

    def __init__(
        self,
        kind: AssignmentKind,
        user_id: UserID,
        current: Amount | Literal[0],
        removed: Amount,
    ) -> None:
        self.kind = kind
        self.user_id = user_id
        self.removed = removed
        self.current = current
        super().__init__()


class NegativeOrZeroAmountError(DomainError):
    value: Decimal | None
    tried: Decimal | float | str

    def __init__(
        self,
        value: Decimal | None,
        tried: Decimal | float | str,
    ) -> None:
        self.value = value
        self.tried = tried
        super().__init__()


class AmountInUseError(DomainError):
    line_item_id: LineItemID
    removed: Amount
    used_by: set[AssignmentKind]
    free_amount: Amount | Literal[0]
    total_amount: Amount

    def __init__(
        self,
        line_item_id: LineItemID,
        removed: Amount,
        used_by: set[AssignmentKind],
        free_amount: Amount | Literal[0],
        total_amount: Amount,
    ) -> None:
        self.line_item_id = line_item_id
        self.removed = removed
        self.used_by = used_by
        self.free_amount = free_amount
        self.total_amount = total_amount
        super().__init__()


class LineItemNotCompatibleError(DomainError):
    """
    Merging not compatible LineItems
    """


class LineItemNotInReceiptError(DomainError):
    line_item_id: LineItemID

    def __init__(self, line_item_id: LineItemID) -> None:
        self.line_item_id = line_item_id
        super().__init__()


class UserNotParticipantError(DomainError):
    user_id: UserID

    def __init__(self, user_id: UserID) -> None:
        self.user_id = user_id


class ReceiptNotFullyFilledError(DomainError): ...
