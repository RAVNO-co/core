from dataclasses import dataclass, field
from typing import Annotated, Literal, NewType

from annotated_types import Gt
from typing_extensions import Doc

from .amount import Amount, Money
from .types import LineItemID, LineItemName, UserID


@dataclass(frozen=True, slots=True)
class Settlement:
    """
    Tuple of items assigned to user
    """

    items: Annotated[
        list[SettlementItem],
        Doc("Mutable with current implementation, but should not be changed"),
    ] = field(default_factory=list)

    @property
    def total(self) -> Money | Literal[0]:
        return sum(i.price * i.amount for i in self.items)


@dataclass(frozen=True, slots=True)
class SettlementItem:
    line_item_id: LineItemID
    name: LineItemName
    amount: Amount
    price: Annotated[Money, Gt(0)]


PaymentTable = NewType("PaymentTable", dict[UserID | None, Settlement])
ConsumptionTable = NewType("ConsumptionTable", dict[UserID | None, Settlement])

DebtorID = UserID
PayerID = UserID
TransactionInstructions = dict[DebtorID, dict[PayerID, Money]]
