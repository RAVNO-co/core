from copy import deepcopy

import pytest

from core.domain.exceptions import (
    LineItemNotCompatibleError,
    NegativeAssignmentError,
    OverAssignmentError,
)
from core.domain.models.line_item import LineItem
from core.domain.value_objects import Amount
from tests.domain.asserts import assert_merged_line_items
from tests.mocks import AssignmentDataFactory, LineItemFactory


def test_consumption_adding(
    line_item: LineItem, assignment_data_factory: AssignmentDataFactory
) -> None:
    assignment = assignment_data_factory(
        max_amount=Amount(line_item.free_amount)
    )

    line_item.add_consumption(**assignment)

    assert (
        line_item.consumptions[assignment["user_id"]] == assignment["amount"]
    )


def test_payment_adding(
    line_item: LineItem, assignment_data_factory: AssignmentDataFactory
) -> None:
    assignment = assignment_data_factory(
        max_amount=Amount(line_item.free_amount)
    )

    line_item.add_payment(**assignment)

    assert line_item.payments[assignment["user_id"]] == assignment["amount"]


def test_consumtion_adding_to_existing_consumer(
    line_item_factory: LineItemFactory,
    assignment_data_factory: AssignmentDataFactory,
) -> None:
    line_item = line_item_factory(min_collection_lenght=1)
    user_id = next(iter(line_item.consumptions.keys()))
    assignment = assignment_data_factory(
        max_amount=Amount(line_item.free_amount),
        user_id=user_id,
    )
    future_amount = (
        line_item.consumptions[assignment["user_id"]] + assignment["amount"]
    )

    line_item.add_consumption(**assignment)

    assert line_item.consumptions[assignment["user_id"]] == future_amount


def test_payment_adding_to_existing_payer(
    line_item_factory: LineItemFactory,
    assignment_data_factory: AssignmentDataFactory,
) -> None:
    line_item = line_item_factory(min_collection_lenght=1)
    user_id = next(iter(line_item.payments.keys()))
    assignment = assignment_data_factory(
        max_amount=Amount(line_item.free_amount),
        user_id=user_id,
    )
    future_amount = (
        line_item.payments[assignment["user_id"]] + assignment["amount"]
    )

    line_item.add_payment(**assignment)

    assert line_item.payments[assignment["user_id"]] == future_amount


def test_full_consumption_removing(line_item_factory: LineItemFactory) -> None:
    line_item = line_item_factory(min_collection_lenght=1)
    user_id = next(iter(line_item.consumptions.keys()))
    amount = line_item.consumptions[user_id]

    line_item.remove_consumption(user_id, amount)

    assert user_id not in line_item.consumptions


def test_full_payment_removing(line_item_factory: LineItemFactory) -> None:
    line_item = line_item_factory(min_collection_lenght=1)
    user_id = next(iter(line_item.payments.keys()))
    amount = line_item.payments[user_id]

    line_item.remove_payment(user_id, amount)

    assert user_id not in line_item.payments


def test_partitial_consumption_removing(
    line_item_factory: LineItemFactory,
    assignment_data_factory: AssignmentDataFactory,
) -> None:
    line_item = line_item_factory(min_collection_lenght=1)
    user_id = next(iter(line_item.consumptions.keys()))
    assignment = assignment_data_factory(
        max_amount=line_item.consumptions[user_id],
        user_id=user_id,
    )
    future_amount = line_item.consumptions[user_id] - assignment["amount"]

    line_item.remove_consumption(**assignment)

    assert line_item.consumptions[user_id] == future_amount


def test_partitial_payment_removing(
    line_item_factory: LineItemFactory,
    assignment_data_factory: AssignmentDataFactory,
) -> None:
    line_item = line_item_factory(min_collection_lenght=1)
    user_id = next(iter(line_item.payments.keys()))
    assignment = assignment_data_factory(
        max_amount=line_item.payments[user_id],
        user_id=user_id,
    )
    future_amount = line_item.payments[user_id] - assignment["amount"]

    line_item.remove_payment(**assignment)

    assert line_item.payments[user_id] == future_amount


def test_passing_can_merge_check(line_item_factory: LineItemFactory) -> None:
    base = line_item_factory()
    to_merge = line_item_factory(name=base.name, price=base.price)

    assert base.can_merge(to_merge)


def test_cant_merge_not_compatible_line_items(
    line_item_factory: LineItemFactory, line_item: LineItem
) -> None:
    to_merge = line_item_factory()

    assert not line_item.can_merge(to_merge)


def test_cant_merge_with_not_line_item(line_item: LineItem) -> None:
    assert not line_item.can_merge(object())


def test_merging(
    line_item_factory: LineItemFactory, line_item: LineItem
) -> None:
    base = deepcopy(line_item)
    to_merge = line_item_factory(name=base.name, price=base.price)

    base += to_merge

    assert_merged_line_items(line_item, base, to_merge)


def test_incopatible_items_merging(
    line_item_factory: LineItemFactory, line_item: LineItem
) -> None:
    to_merge = line_item_factory()

    with pytest.raises(LineItemNotCompatibleError):
        line_item += to_merge


def test_failing_overasigning_consumption_check(
    line_item: LineItem, assignment_data_factory: AssignmentDataFactory
) -> None:
    assignment = assignment_data_factory()
    assignment["amount"] += line_item.total_amount

    with pytest.raises(OverAssignmentError):
        line_item.add_consumption(**assignment)


def test_failing_overasigning_payment_check(
    line_item: LineItem, assignment_data_factory: AssignmentDataFactory
) -> None:
    assignment = assignment_data_factory()
    assignment["amount"] += line_item.total_amount

    with pytest.raises(OverAssignmentError):
        line_item.add_payment(**assignment)


def test_negative_consumption_check(
    line_item_factory: LineItemFactory,
) -> None:
    line_item = line_item_factory(min_collection_lenght=1)
    user_id = next(iter(line_item.consumptions.keys()))
    amount = line_item.consumptions[user_id] + 1

    with pytest.raises(NegativeAssignmentError):
        line_item.remove_consumption(user_id, amount)


def test_negative_payment_check(line_item_factory: LineItemFactory) -> None:
    line_item = line_item_factory(min_collection_lenght=1)
    user_id = next(iter(line_item.payments.keys()))
    amount = line_item.payments[user_id] + 1

    with pytest.raises(NegativeAssignmentError):
        line_item.remove_payment(user_id, amount)


def test_consumer_removing(line_item_factory: LineItemFactory) -> None:
    line_item = line_item_factory(min_collection_lenght=1)
    user_id = next(iter(line_item.consumptions.keys()))

    line_item.remove_consumer(user_id)

    assert user_id not in line_item.consumptions


def test_payer_removing(line_item_factory: LineItemFactory) -> None:
    line_item = line_item_factory(min_collection_lenght=1)
    user_id = next(iter(line_item.payments.keys()))

    line_item.remove_payer(user_id)

    assert user_id not in line_item.payments
