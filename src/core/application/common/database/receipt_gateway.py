from collections.abc import Sequence
from typing import Protocol, TypedDict, Unpack

from core.domain.models import Receipt
from core.domain.value_objects import ReceiptID, UserID


class ReceiptFilters(TypedDict, total=False):
    id: ReceiptID


class ReceiptDBGatewayI(Protocol):
    async def fetch(self, **filters: Unpack[ReceiptFilters]) -> Receipt:
        """Find receipt that satisfies all **filters
        Raises:
            ReceiptNotFoundError: receipt was not found
        """
        ...

    async def fetch_many(
        self,
        user_id: UserID,
        limit: int,
        cursor: ReceiptID | None = None,
        **filters: Unpack[ReceiptFilters]
    ) -> Sequence[Receipt]:
        """Fetch receipts starting from the cursor receipt.
        Returns an empty sequence when none are found.
        Raises:
            CursorNotInListError: cursor not in list
        """
        ...

    async def save(self, receipt: Receipt) -> None:
        """Persist a receipt
        updating an existing record when applicable
        """
        ...


class ReceiptNotFoundError(Exception): ...


class CursorNotInListError(Exception): ...
