from collections import defaultdict
from collections.abc import Generator
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid7

from core.domain.exceptions import ReceiptNotFullyFilledError
from core.domain.models import LineItem, Receipt
from core.domain.models.user import DummyUser, RealUser
from core.domain.value_objects import (
    Amount,
    ConsumptionTable,
    LineItemID,
    LineItemName,
    Money,
    ReceiptID,
    ReceiptTitle,
    Settlement,
    UserID,
    UserNickname,
)
from core.domain.value_objects.settlement import (
    PaymentTable,
    SettlementItem,
    TransactionInstructions,
)


def create_receipt(author: RealUser, title: ReceiptTitle) -> Receipt:
    return Receipt(
        id=ReceiptID(uuid7()),
        title=title,
        author_id=author.id,
        created_at=datetime.now(UTC),
        participant_ids={author.id},
    )


def create_line_item(
    name: LineItemName,
    amount: Amount,
    price: Money,
) -> LineItem:
    return LineItem(
        id=LineItemID(uuid7()), name=name, total_amount=amount, price=price
    )


def create_dummy_user(nickname: UserNickname) -> DummyUser:
    return DummyUser(id=UserID(uuid7()), nickname=nickname)


def create_real_user(nickname: UserNickname) -> RealUser:
    return RealUser(id=UserID(uuid7()), nickname=nickname)


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


def form_consumption_table(receipt: Receipt) -> ConsumptionTable:
    return ConsumptionTable(_form_settlement_table(receipt, "consumptions"))


def form_payment_table(receipt: Receipt) -> PaymentTable:
    return PaymentTable(_form_settlement_table(receipt, "payments"))


def form_transaction_instructions(receipt: Receipt) -> TransactionInstructions:
    if not receipt.is_filled:
        raise ReceiptNotFullyFilledError
    if not receipt.items:
        return {}

    instructions: TransactionInstructions = defaultdict(dict)

    def summarize_settlement(
        table: PaymentTable | ConsumptionTable,
    ) -> Generator[tuple[UserID, Decimal]]:
        return (
            (user_id, Decimal(settlement.total))
            for user_id, settlement in table.items()
            if user_id is not None
        )

    payment_generator = summarize_settlement(form_payment_table(receipt))
    debt_generator = summarize_settlement(form_consumption_table(receipt))

    debtor_id, debt = next(debt_generator)
    for payer_id, total_payed in payment_generator:
        to_return = total_payed

        while to_return > 0:
            returned = min(to_return, debt)
            instructions[debtor_id][payer_id] = Money(returned)

            to_return -= returned
            debt -= returned

            if debt == 0 and to_return != 0:
                debtor_id, debt = next(debt_generator)

    return instructions
