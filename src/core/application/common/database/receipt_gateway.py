from typing import Protocol, TypedDict, Unpack

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
        """Saves new receipt or updates one with the same id"""
        ...


class ReceiptNotFoundError(Exception): ...
