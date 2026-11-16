import asyncio
from dataclasses import dataclass
from typing import final
from collections.abc import Sequence

from core.application.common import Interactor
from core.application.common.database import (
    ReceiptMultipleDBGatewayI,
    UserDBGatewayI,
)
from core.application.common.user_id_provider import UserIDProviderI
from core.domain.models import Receipt

@dataclass(frozen=True, slots=True)
class ListReceiptDTO: 
    page_size: int | None
    page_index: int | None

@dataclass(frozen=True, slots=True)
class ListReceiptResultDTO: 
    receipts: Sequence[Receipt]

@final
@dataclass(frozen=True, slots=True)
class ListReceipt(Interactor[ListReceiptDTO, ListReceiptResultDTO]):
    receipt_multiple_db_gateway: ReceiptMultipleDBGatewayI
    user_db_gateway: UserDBGatewayI
    user_id_provider: UserIDProviderI

    async def __call__(
        self, context: ListReceiptDTO
        ) -> ListReceiptResultDTO:
        user_id = self.user_id_provider.get_current_user_id()
        receipts = await self.receipt_multiple_db_gateway.fetch_page(context.page_size,context.page_index,user_id)

        return ListReceiptResultDTO(receipts)
