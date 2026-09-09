from uuid import uuid7

from core.domain.models import LineItem
from core.domain.value_objects import Amount, LineItemID, LineItemName, Money


class CreateLineItem:
    def __call__(
        self, name: LineItemName, amount: Amount, price: Money
    ) -> LineItem:
        return LineItem(
            id=LineItemID(uuid7()),
            name=name,
            total_amount=amount,
            price=price,
        )
