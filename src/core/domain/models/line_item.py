from dataclasses import dataclass, field
from typing import Literal, Self

from core.domain.exceptions import (
    AmountInUseError,
    LineItemNotCompatibleError,
)
from core.domain.models.assignment import (
    Assignment,
    AssignmentProxy,
)
from core.domain.value_objects import (
    Amount,
    AssignmentKind,
    LineItemID,
    LineItemName,
    Money,
    UserID,
)


@dataclass
class LineItem:
    id: LineItemID

    name: LineItemName
    total_amount: Amount
    price: Money

    _consumptions: Assignment = field(
        default_factory=lambda: Assignment(AssignmentKind.CONSUMER)
    )
    _payments: Assignment = field(
        default_factory=lambda: Assignment(AssignmentKind.PAYER)
    )

    @property
    def consumptions(self) -> AssignmentProxy:
        return self._consumptions.values

    @property
    def payments(self) -> AssignmentProxy:
        return self._payments.values

    @property
    def is_filled(self) -> bool:
        return not self.free_amount

    @property
    def free_amount(self) -> Amount | Literal[0]:
        used = max(self._consumptions.total, self._payments.total)
        if used == self.total_amount:
            return 0
        return Amount(
            self.total_amount
            - max(self._consumptions.total, self._payments.total)
        )

    def reduce_amount(self, amount: Amount) -> None:
        if amount > self.free_amount:
            used_by = {
                i[0]
                for i in (
                    (AssignmentKind.CONSUMER, self._consumptions.total),
                    (AssignmentKind.PAYER, self._payments.total),
                )
                if amount > i[1]
            }
            raise AmountInUseError(
                line_item_id=self.id,
                removed=amount,
                used_by=used_by,
                free_amount=self.free_amount,
                total_amount=self.total_amount,
            )

        self.total_amount = Amount(self.total_amount - amount)

    def add_consumption(self, user_id: UserID, amount: Amount) -> None:
        self._consumptions.assign(user_id, amount, self.total_amount)

    def add_payment(self, user_id: UserID, amount: Amount) -> None:
        self._payments.assign(user_id, amount, self.total_amount)

    def remove_consumption(self, user_id: UserID, amount: Amount) -> None:
        self._consumptions.remove(user_id, amount)

    def remove_consumer(self, user_id: UserID) -> None:
        amount = self._consumptions.values.get(user_id, None)
        if amount is not None:
            self._consumptions.remove(user_id, amount)

    def remove_payment(self, user_id: UserID, amount: Amount) -> None:
        self._payments.remove(user_id, amount)

    def remove_payer(self, user_id: UserID) -> None:
        amount = self._payments.values.get(user_id, None)
        if amount is not None:
            self._payments.remove(user_id, amount)

    def can_merge(self, value: object, /) -> bool:
        if not isinstance(value, LineItem):
            return False
        return self.name == value.name and self.price == value.price

    def __iadd__(self, other: object, /) -> Self:
        if not isinstance(other, LineItem) or not self.can_merge(other):
            raise LineItemNotCompatibleError
        self.total_amount = Amount(other.total_amount + self.total_amount)

        for user_id, amount in other.consumptions.items():
            self.add_consumption(user_id, amount)
        for user_id, amount in other.payments.items():
            self.add_payment(user_id, amount)

        return self
