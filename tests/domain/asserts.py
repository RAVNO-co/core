from typing import Literal, Unpack

from core.domain.models import Receipt
from core.domain.models.line_item import LineItem
from core.domain.value_objects import Settlement, UserID
from tests.mocks import LineItemData


def assert_merged_line_items(
    initial: LineItem, base: LineItem, to_merge: LineItem
) -> None:
    assert base.id == initial.id
    assert base.name == initial.name
    assert base.price == initial.price
    assert base.total_amount == initial.total_amount + to_merge.total_amount

    for user_id in base.payments:
        assert base.payments[user_id] == (
            initial.payments.get(user_id, 0)
            + to_merge.payments.get(user_id, 0)
        )

    for user_id in base.consumptions:
        assert base.consumptions[user_id] == (
            initial.consumptions.get(user_id, 0)
            + to_merge.consumptions.get(user_id, 0)
        )


def assert_compare_line_items(
    initial: LineItem, other: LineItem, **other_rewrites: Unpack[LineItemData]
) -> None:
    assert initial.id == other_rewrites.get("id", other.id)
    assert initial.name == other_rewrites.get("name", other.name)
    assert initial.price == other_rewrites.get("price", other.price)
    assert initial.total_amount == other_rewrites.get(
        "total_amount", other.total_amount
    )

    for user_id in initial.payments:
        assert (
            initial.payments[user_id]
            == other_rewrites.get("payments", other.payments)[user_id]
        )
    for user_id in initial.consumptions:
        assert (
            initial.consumptions[user_id]
            == other_rewrites.get("consumptions", other.consumptions)[user_id]
        )


def assert_matched_settlements_and_assignes(
    settlements: dict[UserID | None, Settlement],
    receipt: Receipt,
    collection: Literal["consumptions", "payments"],
) -> None:
    for user_id, settlement in settlements.items():
        for item in settlement.items:
            if user_id is None:
                # if all settled values match unsettled values will match too
                continue
            assert (
                getattr(receipt._items[item.line_item_id], collection)[user_id]  # ruff: ignore[private-member-access]
                == item.amount
            )
