from collections.abc import Sequence
from typing import Protocol, TypedDict, Unpack

from core.domain.models import Receipt
from core.domain.value_objects import ReceiptID, UserID


class ReceiptFilters(TypedDict, total=False):
    id: ReceiptID


class ManyReceiptFilters(TypedDict, total=False):
    participant_ids: Sequence[UserID]


class ReceiptDBGatewayI(Protocol):
    async def fetch(self, **filters: Unpack[ReceiptFilters]) -> Receipt:
        """Find receipt that satisfies all **filters
        Raises:
            ReceiptNotFoundError: receipt was not found
        """
        ...

    async def fetch_many(
        self,
        /,
        limit: int,
        cursor: ReceiptID | None = None,
        **filters: Unpack[ManyReceiptFilters]
    ) -> Sequence[Receipt]:
        """Fetch receipts starting from the cursor receipt.
        Returns an empty sequence when none are found.
        """
        ...

    async def save(self, receipt: Receipt) -> None:
        """Persist a receipt
        updating an existing record when applicable
        """
        ...


class ReceiptNotFoundError(Exception): ...
