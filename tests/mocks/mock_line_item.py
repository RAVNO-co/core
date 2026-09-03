from typing import Any, Protocol, TypedDict, Unpack

import pytest
from mimesis import Field, Schema
from mimesis.types import CallableSchema

from core.domain.models import LineItem
from core.domain.services import create_line_item
from core.domain.value_objects import (
    Amount,
    LineItemID,
    LineItemName,
    Money,
    UserID,
)

from .mock_assignment import assignment_schema_factory


class LineItemData(TypedDict, total=False):
    id: LineItemID
    name: LineItemName
    total_amount: Amount
    price: Money
    consumptions: dict[UserID, Amount]
    payments: dict[UserID, Amount]


class LineItemDataFactory(Protocol):
    def __call__(
        self, min_collection_lenght: int = 0, **fields: Unpack[LineItemData]
    ) -> LineItemData: ...


class LineItemFactory(Protocol):
    def __call__(
        self, min_collection_lenght: int = 0, **fields: Unpack[LineItemData]
    ) -> LineItem: ...


def line_item_schema_factory(
    field: Field, min_collection_lenght: int
) -> CallableSchema:
    assignment_schema = assignment_schema_factory(field)

    def bulk_assignment_schema() -> dict[UserID, Amount]:
        return {
            assignment["user_id"]: assignment["amount"]
            for assignment in (
                assignment_schema()
                for _ in range(
                    field(
                        "integer_number", start=min_collection_lenght, end=100
                    )
                )
            )
        }

    def schema() -> dict[str, Any]:
        consumers = bulk_assignment_schema()
        payers = bulk_assignment_schema()
        total_amount = assignment_schema()["amount"] + max(
            sum(consumers.values()), sum(payers.values())
        )
        return {
            "id": LineItemID(field("uuid")),
            "name": LineItemName(field("word")),
            "total_amount": total_amount,
            "price": Money(field("price", minimum=0.01, as_decimal=True)),
            "consumptions": consumers,
            "payments": payers,
        }

    return schema


@pytest.fixture
def line_item_data_factory() -> LineItemDataFactory:
    field = Field()

    def factory(
        min_collection_lenght: int = 0, **fields: Unpack[LineItemData]
    ) -> LineItemData:
        field.reseed()
        schema = Schema(
            schema=line_item_schema_factory(field, min_collection_lenght),
            iterations=1,
        )
        return {**schema.create()[0], **fields}  # type:ignore[typeddict-item]

    return factory


@pytest.fixture
def line_item_data(
    line_item_data_factory: LineItemDataFactory,
) -> LineItemData:
    return line_item_data_factory()


def map_mock_line_item(data: LineItemData) -> LineItem:
    item = create_line_item(data["name"], data["total_amount"], data["price"])
    for consumer_id, amount in data["consumptions"].items():
        item.add_consumption(consumer_id, amount)
    for consumer_id, amount in data["payments"].items():
        item.add_payment(consumer_id, amount)
    return item


@pytest.fixture
def line_item_factory(
    line_item_data_factory: LineItemDataFactory,
) -> LineItemFactory:
    def factory(
        min_collection_lenght: int = 0, **fields: Unpack[LineItemData]
    ) -> LineItem:
        data = line_item_data_factory(
            min_collection_lenght=min_collection_lenght, **fields
        )
        return map_mock_line_item(data)

    return factory


@pytest.fixture
def line_item(
    line_item_factory: LineItemFactory,
) -> LineItem:
    return line_item_factory()
