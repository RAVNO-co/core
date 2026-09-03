from collections.abc import Callable
from typing import Any, Protocol, TypedDict, Unpack

import pytest
from mimesis import Field, Schema
from mimesis.types import JSON

from core.domain.value_objects import Amount, UserID

DEFAULT_MAX_AMOUNT = Amount(1500)


class AssignmentData(TypedDict, total=False):
    user_id: UserID
    amount: Amount


class AssignmentDataFactory(Protocol):
    def __call__(
        self,
        max_amount: Amount = DEFAULT_MAX_AMOUNT,
        **fields: Unpack[AssignmentData],
    ) -> AssignmentData: ...


def assignment_schema_factory(
    field: Field, max_amount: Amount = DEFAULT_MAX_AMOUNT
) -> Callable[..., JSON]:
    def schema() -> dict[str, Any]:
        minimum = 0.01
        maximum = float(max_amount) - minimum  # exclude max value from range
        return {
            "user_id": UserID(field("uuid")),
            "amount": Amount(
                field(
                    "price",
                    minimum=minimum,
                    maximum=maximum,
                    as_decimal=True,
                )
            ),
        }

    return schema


@pytest.fixture
def assignment_data_factory() -> AssignmentDataFactory:
    def factory(
        max_amount: Amount = DEFAULT_MAX_AMOUNT,
        **fields: Unpack[AssignmentData],
    ) -> AssignmentData:
        field = Field()
        schema = Schema(
            assignment_schema_factory(field, max_amount),
            iterations=1,
        )
        return {**schema.create()[0], **fields}  # type:ignore[typeddict-item]

    return factory


@pytest.fixture
def assignment_data(
    assignment_data_factory: AssignmentDataFactory,
) -> AssignmentData:
    return assignment_data_factory()
