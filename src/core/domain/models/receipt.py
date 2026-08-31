from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Annotated

from annotated_types import Timezone
from typing_extensions import Doc

from core.domain.exceptions import (
    LineItemNotInReceiptError,
    UserNotParticipantError,
)
from core.domain.models.line_item import LineItem
from core.domain.value_objects import (
    Amount,
    LineItemID,
    ReceiptID,
    ReceiptTitle,
    UserID,
)


@dataclass
class Receipt:
    id: ReceiptID
    title: ReceiptTitle
    author_id: UserID
    created_at: Annotated[datetime, Timezone(...)]

    participant_ids: Annotated[set[UserID], Doc("author_id included")]
    _items: dict[LineItemID, LineItem] = field(default_factory=dict)

    @property
    def items(self) -> Iterable[LineItem]:
        return self._items.values()

    @property
    def is_filled(self) -> bool:
        return all(i.is_filled for i in self.items)

    def append_participant(self, user_id: UserID) -> None:
        self.participant_ids.add(user_id)

    def remove_participant(self, user_id: UserID) -> None:
        self._check_user_participant(user_id)
        for item in self._items.values():
            item.remove_consumer(user_id)
            item.remove_payer(user_id)
        self.participant_ids.remove(user_id)

    def append_item(self, line_item: LineItem) -> None:
        for payer_id in line_item.payments:
            self._check_user_participant(payer_id)
        for consumer_id in line_item.consumptions:
            self._check_user_participant(consumer_id)

        existing_item = next(
            (
                item
                for item in self._items.values()
                if item.can_merge(line_item)
            ),
            None,
        )
        if existing_item is not None:
            existing_item += line_item
            return

        self._items[line_item.id] = line_item

    def remove_item(self, line_item_id: LineItemID, amount: Amount) -> None:
        item = self._find_existing_item(line_item_id)
        if amount == item.free_amount == item.total_amount:
            del self._items[line_item_id]
            return

        item.reduce_amount(amount)

    def assign_consumption(
        self, line_item_id: LineItemID, user_id: UserID, amount: Amount
    ) -> None:
        self._check_user_participant(user_id)
        self._find_existing_item(line_item_id).add_consumption(user_id, amount)

    def assign_payment(
        self, line_item_id: LineItemID, user_id: UserID, amount: Amount
    ) -> None:
        self._check_user_participant(user_id)
        self._find_existing_item(line_item_id).add_payment(user_id, amount)

    def disassign_consumption(
        self, line_item_id: LineItemID, user_id: UserID, amount: Amount
    ) -> None:
        self._check_user_participant(user_id)
        self._find_existing_item(line_item_id).remove_consumption(
            user_id, amount
        )

    def disassign_payment(
        self, line_item_id: LineItemID, user_id: UserID, amount: Amount
    ) -> None:
        self._check_user_participant(user_id)
        self._find_existing_item(line_item_id).remove_payment(user_id, amount)

    def _check_user_participant(self, user_id: UserID) -> None:
        if user_id not in self.participant_ids:
            raise UserNotParticipantError(user_id)

    def _find_existing_item(self, line_item_id: LineItemID) -> LineItem:
        if line_item_id not in self._items:
            raise LineItemNotInReceiptError(line_item_id)
        return self._items[line_item_id]
