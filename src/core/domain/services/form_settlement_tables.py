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
    table: defaultdict[UserID | None, Settlement] = defaultdict(Settlement)
    unsettled = Settlement()
    for item in receipt.items:
        settled_amount = 0
        for user_id, amount in getattr(item, collection).items():
            settled_amount += amount
            settlement = SettlementItem(item.id, item.name, amount, item.price)
            table[user_id].items.append(settlement)
        if item.total_amount > settled_amount:
            unsettled.items.append(
                SettlementItem(
                    item.id,
                    item.name,
                    Amount(item.total_amount - settled_amount),
                    item.price,
                )
            )
    table[None] = unsettled
    return table


class FormPaymentTable:
    def __call__(self, receipt: Receipt) -> PaymentTable:
        return PaymentTable(_form_settlement_table(receipt, "payments"))


class FormConsumptionTable:
    def __call__(self, receipt: Receipt) -> ConsumptionTable:
        return ConsumptionTable(
            _form_settlement_table(receipt, "consumptions")
        )
