from typing import Protocol, TypedDict, Unpack
from collections.abc import Sequence

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
            cursor: ReceiptID,
            ) -> Sequence[Receipt]:
        """Fetch a receipt list starting from cursor receipt. Returns empty list, if no receipts found
        Raises:
            UserNotFoundError: user was not found
            CursorNotInListError: cursor not in list
        """
        ...

    async def save(self, receipt: Receipt) -> None:
        """Persist a receipt
        updating an existing record when applicable
        """
        ...

class ReceiptNotFoundError(Exception): ...
class UserNotFoundError(Exception): ...
class CursorNotInListError(Exception): ...
