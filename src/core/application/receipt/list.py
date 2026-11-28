from collections.abc import Sequence
from dataclasses import dataclass
from typing import final

from core.application.common import Interactor
from core.application.common.database import (
    ReceiptDBGatewayI,
)
from core.application.common.user_id_provider import UserIDProviderI
from core.domain.models import Receipt
from core.domain.value_objects import ReceiptID


@dataclass(frozen=True, slots=True)
class ListReceiptDTO:
    cursor: ReceiptID | None
    limit: int


@dataclass(frozen=True, slots=True)
class ListReceiptResultDTO:
    receipts: Sequence[Receipt]


@final
@dataclass(frozen=True, slots=True)
class ListReceipt(Interactor[ListReceiptDTO, ListReceiptResultDTO]):
    receipt_db_gateway: ReceiptDBGatewayI
    user_id_provider: UserIDProviderI

    async def __call__(self, context: ListReceiptDTO) -> ListReceiptResultDTO:
        participant_id = self.user_id_provider.get_current_user_id()
        receipts = await self.receipt_db_gateway.fetch_many(
            context.limit, context.cursor, participant_ids=[participant_id]
        )

        return ListReceiptResultDTO(receipts)
