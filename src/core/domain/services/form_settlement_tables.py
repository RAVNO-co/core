from collections import defaultdict

from core.domain.models import Receipt
from core.domain.value_objects import (
    Amount,
    ConsumptionTable,
    Settlement,
    UserID,
)
from core.domain.value_objects.settlement import PaymentTable, SettlementItem


def _form_settlement_table(
    receipt: Receipt, collection: str
) -> dict[UserID | None, Settlement]:
    mutable_table: defaultdict[UserID | None, list[SettlementItem]] = (
        defaultdict(list)
    )
    unsettled: list[SettlementItem] = []
    for item in receipt.items:
        settled_amount = 0
        for user_id, amount in getattr(item, collection).items():
            settled_amount += amount
            settlement = SettlementItem(item.id, item.name, amount, item.price)
            mutable_table[user_id].append(settlement)
        if item.total_amount > settled_amount:
            unsettled.append(
                SettlementItem(
                    item.id,
                    item.name,
                    Amount(item.total_amount - settled_amount),
                    item.price,
                )
            )
    mutable_table[None] = unsettled

    return {
        user_id: Settlement(items) for user_id, items in mutable_table.items()
    }


class FormPaymentTable:
    def __call__(self, receipt: Receipt) -> PaymentTable:
        return PaymentTable(_form_settlement_table(receipt, "payments"))


class FormConsumptionTable:
    def __call__(self, receipt: Receipt) -> ConsumptionTable:
        return ConsumptionTable(
            _form_settlement_table(receipt, "consumptions")
        )
