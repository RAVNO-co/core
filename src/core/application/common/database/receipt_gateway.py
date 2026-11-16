from typing import Protocol, TypedDict, Unpack
from collections.abc import Sequence

from core.domain.models import Receipt
from core.domain.value_objects import ReceiptID


class ReceiptFilters(TypedDict, total=False):
    id: ReceiptID


class ReceiptDBGatewayI(Protocol):
    async def fetch(self, **filters: Unpack[ReceiptFilters]) -> Receipt:
        """Find receipt that satisfies all **filters
        Raises:
            ReceiptNotFoundError: receipt was not found
        """
        ...

    async def save(self, receipt: Receipt) -> None:
        """Persist a receipt
        updating an existing record when applicable
        """
        ...

class ReceiptMultipleDBGatewayI(Protocol):
    async def fetch_page(
            self,
            user_id,
            page_size,
            page_index,
            ) -> Sequence[Receipt]:
        """Fetch a receipt list of page_size containing user_id, page_index used for pagination. Returns empty list, if no receipts found
        Raises:
            UserNotFoundError: user was not found
            PageOutOfBoundsError: page out of bounds error
        """
        ...

class ReceiptNotFoundError(Exception): ...
