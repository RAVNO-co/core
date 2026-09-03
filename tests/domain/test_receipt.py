from copy import deepcopy
from typing import cast

import pytest

from core.domain.exceptions import UserNotParticipantError
from core.domain.models import RealUser, Receipt
from core.domain.value_objects import Amount
from tests.mocks import (
    AssignmentDataFactory,
    LineItemDataFactory,
    LineItemFactory,
    ReceiptFactory,
)

from .asserts import (
    assert_compare_line_items,
    assert_merged_line_items,
)


def test_participant_appending(receipt: Receipt, real_user: RealUser) -> None:
    receipt.append_participant(real_user.id)

    assert real_user.id in receipt.participant_ids


def test_participant_delition(receipt_factory: ReceiptFactory) -> None:
    receipt = receipt_factory(min_collection_lenght=1)
    participant_id = next(iter(receipt.participant_ids))

    receipt.remove_participant(participant_id)

    assert participant_id not in receipt.participant_ids
    for line_item in receipt.items:
        assert participant_id not in line_item.payments
        assert participant_id not in line_item.consumptions


def test_item_appending(
    line_item_factory: LineItemFactory, receipt: Receipt
) -> None:
    line_item = line_item_factory(payments={}, consumptions={})

    receipt.append_item(line_item)

    assert line_item in receipt.items


def test_item_appending_with_merge(
    line_item_factory: LineItemFactory, receipt_factory: ReceiptFactory
) -> None:
    receipt = receipt_factory(min_collection_lenght=1)
    base = next(iter(receipt.items))
    initial = deepcopy(base)
    to_merge = line_item_factory(
        name=base.name,
        price=base.price,
        consumptions={},
        payments={},
    )

    receipt.append_item(to_merge)

    assert_merged_line_items(initial, base, to_merge)


def test_item_appending_participant_check(
    line_item_factory: LineItemFactory, receipt: Receipt
) -> None:
    line_item = line_item_factory(min_collection_lenght=1)

    with pytest.raises(UserNotParticipantError):
        receipt.append_item(line_item)


def test_partitial_item_delition(
    receipt_factory: ReceiptFactory,
    assignment_data_factory: AssignmentDataFactory,
) -> None:
    receipt = receipt_factory(min_collection_lenght=1)
    line_item = next(iter(receipt.items))
    initital_line_item = deepcopy(line_item)
    amount = assignment_data_factory(
        max_amount=cast(Amount, line_item.free_amount)
    )["amount"]

    receipt.remove_item(line_item.id, amount)

    assert_compare_line_items(
        initital_line_item,
        line_item,
        total_amount=initital_line_item.total_amount,
    )
    assert line_item.total_amount + amount == initital_line_item.total_amount


def test_full_item_delition(
    line_item_data_factory: LineItemDataFactory,
    receipt_factory: ReceiptFactory,
) -> None:
    receipt = receipt_factory(
        items=(line_item_data_factory(payments={}, consumptions={}),)
    )
    line_item = next(iter(receipt.items))

    receipt.remove_item(line_item.id, line_item.total_amount)

    assert line_item not in receipt.items


def test_consumption_assigning(
    receipt_factory: ReceiptFactory,
) -> None:
    receipt = receipt_factory(min_collection_lenght=1)
    line_item = next(iter(receipt.items))
    user_id, amount = (
        next(iter(receipt.participant_ids)),
        Amount(line_item.free_amount),
    )
    initial = deepcopy(line_item)

    receipt.assign_consumption(line_item.id, user_id, amount)

    assert line_item.consumptions[
        user_id
    ] == amount + initial.consumptions.get(user_id, 0)
    assert_compare_line_items(
        initial,
        line_item,
        consumptions={
            **line_item.consumptions,
            user_id: initial.consumptions.get(user_id, amount),
        },
    )


def test_consumption_disassigning(
    receipt_factory: ReceiptFactory,
) -> None:
    receipt = receipt_factory(min_collection_lenght=1)
    line_item = next(iter(receipt.items))
    initial = deepcopy(line_item)
    user_id, amount = next(iter(line_item.consumptions.items()))

    receipt.unassign_consumption(line_item.id, user_id, amount)

    assert user_id not in line_item.consumptions
    assert_compare_line_items(line_item, initial)


def test_payment_assigning(
    receipt_factory: ReceiptFactory,
) -> None:
    receipt = receipt_factory(min_collection_lenght=1)
    line_item = next(iter(receipt.items))
    user_id, amount = (
        next(iter(receipt.participant_ids)),
        Amount(line_item.free_amount),
    )
    initial = deepcopy(line_item)

    receipt.assign_payment(line_item.id, user_id, amount)

    assert line_item.payments[user_id] == amount + initial.payments.get(
        user_id, 0
    )
    assert_compare_line_items(
        initial,
        line_item,
        payments={
            **line_item.payments,
            user_id: initial.payments.get(user_id, amount),
        },
    )


def test_payment_disassigning(
    receipt_factory: ReceiptFactory,
) -> None:
    receipt = receipt_factory(min_collection_lenght=1)
    line_item = next(iter(receipt.items))
    initial = deepcopy(line_item)
    user_id, amount = next(iter(line_item.payments.items()))

    receipt.unassign_payment(line_item.id, user_id, amount)

    assert user_id not in line_item.payments
    assert_compare_line_items(line_item, initial)
