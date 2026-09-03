from collections.abc import Iterable
from datetime import datetime
from typing import Annotated, Any, Protocol, TypedDict, Unpack, cast

import pytest
from annotated_types import Timezone
from mimesis import Field, Schema
from mimesis.types import CallableSchema

from core.domain.models.receipt import Receipt
from core.domain.services import create_receipt
from core.domain.value_objects.types import ReceiptID, ReceiptTitle, UserID
from tests.mocks.mock_user import RealUserFactory

from .mock_line_item import (
    LineItemData,
    line_item_schema_factory,
    map_mock_line_item,
)


class ReceiptData(TypedDict, total=False):
    id: ReceiptID
    title: ReceiptTitle
    author_id: UserID
    created_at: Annotated[datetime, Timezone(...)]

    participant_ids: set[UserID]
    items: Iterable[LineItemData]


class ReceiptDataFactory(Protocol):
    def __call__(
        self, min_collection_lenght: int = 0, **fields: Unpack[ReceiptData]
    ) -> ReceiptData: ...


class ReceiptFactory(Protocol):
    def __call__(
        self, min_collection_lenght: int = 0, **fields: Unpack[ReceiptData]
    ) -> Receipt: ...


def receipt_schema_factory(
    field: Field, min_collection_lenght: int
) -> CallableSchema:
    line_item_schema = line_item_schema_factory(field, min_collection_lenght)

    def bulk_line_item_schema() -> tuple[LineItemData, ...]:
        return tuple(
            item
            for item in (
                cast(LineItemData, line_item_schema())
                for _ in range(
                    field(
                        "integer_number", start=min_collection_lenght, end=100
                    )
                )
            )
        )

    def schema() -> dict[str, Any]:
        items = bulk_line_item_schema()

        participant_ids: list[UserID] = []
        for item in items:
            participant_ids.extend(item["payments"].keys())
            participant_ids.extend(item["consumptions"].keys())

        return {
            "id": ReceiptID(field("uuid")),
            "title": ReceiptTitle(field("sentence")),
            "author_id": next(iter([*participant_ids, UserID(field("uuid"))])),
            "created_at": field("datetime", timezone="UTC"),
            "participant_ids": set(participant_ids),
            "items": items,
        }

    return schema


@pytest.fixture
def receipt_data_factory() -> ReceiptDataFactory:
    def factory(
        min_collection_lenght: int = 0, **fields: Unpack[ReceiptData]
    ) -> ReceiptData:
        field = Field()
        schema = Schema(
            schema=receipt_schema_factory(field, min_collection_lenght),
            iterations=1,
        )
        return {**schema.create()[0], **fields}  # type:ignore[typeddict-item]

    return factory


@pytest.fixture
def receipt_data(receipt_data_factory: ReceiptDataFactory) -> ReceiptData:
    return receipt_data_factory()


@pytest.fixture
def receipt_factory(
    receipt_data_factory: ReceiptDataFactory,
    real_user_factory: RealUserFactory,
) -> ReceiptFactory:
    def factory(
        min_collection_lenght: int = 0, **fields: Unpack[ReceiptData]
    ) -> Receipt:
        data = receipt_data_factory(min_collection_lenght, **fields)
        author = real_user_factory(id=data["author_id"])

        receipt = create_receipt(author, data["title"])
        receipt.id = data["id"]
        receipt.created_at = data["created_at"]

        for participant_id in data["participant_ids"]:
            receipt.append_participant(participant_id)

        for item in data["items"]:
            receipt.append_item(map_mock_line_item(item))

        return receipt

    return factory


@pytest.fixture
def receipt(receipt_factory: ReceiptFactory) -> Receipt:
    return receipt_factory()
