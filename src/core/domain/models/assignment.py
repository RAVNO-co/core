from dataclasses import dataclass, field
from decimal import Decimal
from functools import cached_property
from types import MappingProxyType
from typing import Literal

from core.domain.exceptions import NegativeAssignmentError, OverAssignmentError
from core.domain.value_objects import Amount, AssignmentKind, UserID

AssignmentProxy = MappingProxyType[UserID, Amount]


@dataclass
class Assignment:
    kind: AssignmentKind
    _values: dict[UserID, Amount] = field(default_factory=dict)

    @property
    def values(self) -> AssignmentProxy:
        return MappingProxyType(self._values)

    @cached_property
    def total(self) -> Amount | Literal[0]:
        return sum(self._values.values())

    def assign(self, user_id: UserID, amount: Amount, limit: Amount) -> None:
        if self.total + amount > limit:
            raise OverAssignmentError(
                kind=self.kind,
                user_id=user_id,
                current=self.total,
                added=amount,
                limit=limit,
            )

        self._values[user_id] = Amount(
            self._values.get(user_id, Decimal(0)) + amount
        )
        self._reset_total()

    def remove(self, user_id: UserID, amount: Amount) -> None:
        new_value = Decimal(self._values.get(user_id, 0)) - amount

        if new_value < 0:
            raise NegativeAssignmentError(
                kind=self.kind,
                user_id=user_id,
                current=self.total,
                removed=amount,
            )
        if new_value == 0 and user_id in self._values:
            del self._values[user_id]
            return

        self._values[user_id] = Amount(new_value)
        self._reset_total()

    def _reset_total(self) -> None:
        if hasattr(self, "total"):
            del self.total
