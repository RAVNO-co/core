import pytest

from core.domain.exceptions import ReceiptNotFullyFilledError
from core.domain.models import Receipt
from core.domain.services import (
    create_dummy_user,
    create_line_item,
    create_real_user,
    create_receipt,
    form_consumption_table,
    form_payment_table,
    form_transaction_instructions,
)
from tests.domain.asserts import assert_matched_settlements_and_assignes
from tests.domain.setups import fulfill_receipt
from tests.mocks import (
    LineItemData,
    RealUserFactory,
    ReceiptData,
    ReceiptFactory,
    UserData,
)


def test_dummy_user_cretion(user_data: UserData) -> None:
    dummy = create_dummy_user(user_data["nickname"])

    assert dummy.nickname == user_data["nickname"]


def test_real_user_creation(user_data: UserData) -> None:
    real = create_real_user(user_data["nickname"])

    assert real.nickname == user_data["nickname"]


def test_create_line_item_service(
    line_item_data: LineItemData,
) -> None:
    line_item = create_line_item(
        line_item_data["name"],
        line_item_data["total_amount"],
        line_item_data["price"],
    )

    assert line_item.name == line_item_data["name"]
    assert line_item.total_amount == line_item_data["total_amount"]
    assert line_item.price == line_item_data["price"]
    assert not line_item.payments
    assert not line_item.consumptions


def test_receipt_creation(
    real_user_factory: RealUserFactory, receipt_data: ReceiptData
) -> None:
    author = real_user_factory(id=receipt_data["author_id"])

    receipt = create_receipt(author, receipt_data["title"])

    assert receipt.author_id == author.id
    assert len(receipt.participant_ids) == 1
    assert receipt.participant_ids.pop() == author.id
    assert not receipt.items


def test_consuption_table_forming(receipt: Receipt) -> None:
    settlements = form_consumption_table(receipt)

    assert_matched_settlements_and_assignes(
        settlements, receipt, "consumptions"
    )


def test_payment_table_forming(receipt: Receipt) -> None:
    settlements = form_payment_table(receipt)

    assert_matched_settlements_and_assignes(settlements, receipt, "payments")


def test_transaction_intructions_dont_make_debtors_overpay(
    receipt: Receipt,
) -> None:
    receipt = fulfill_receipt(receipt)

    instructions = form_transaction_instructions(receipt)

    consumption_table = form_consumption_table(receipt)
    for user_id in instructions:
        assert (
            sum(instructions[user_id].values())
            == consumption_table[user_id].total
        )


def test_transaction_intructions_cover_all_payments(
    receipt_factory: ReceiptFactory,
) -> None:
    receipt = fulfill_receipt(receipt_factory(min_collection_lenght=1))

    instructions = form_transaction_instructions(receipt)

    total_payments = sum(
        settlement.total for settlement in form_payment_table(receipt).values()
    )
    transactions_sum = sum(
        sum(transaction.values()) for transaction in instructions.values()
    )
    assert total_payments == transactions_sum


def test_transiction_intructioins_is_filled_check(
    receipt_factory: ReceiptFactory,
) -> None:
    with pytest.raises(ReceiptNotFullyFilledError):
        _ = form_transaction_instructions(
            receipt_factory(min_collection_lenght=5)
        )
