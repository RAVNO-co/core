from dataclasses import dataclass
from typing import final

from core.application.common.database.receipt_gateway import ReceiptDBGatewayI
from core.application.common.database.transaction_manager import (
    TransactionManagerI,
)
from core.application.common.database.user_gateway import UserDBGatewayI
from core.application.common.interactor import Interactor
from core.application.common.user_id_provider import UserIDProviderI
from core.domain.value_objects.types import ReceiptID


@dataclass(frozen=True, slots=True)
class JoinReceiptDTO:
    receipt_id: ReceiptID


@final
@dataclass(frozen=True, slots=True)
class JoinReceipt(Interactor[JoinReceiptDTO, None]):
    transaction_manager: TransactionManagerI
    receipt_db_gateway: ReceiptDBGatewayI
    user_db_gateway: UserDBGatewayI
    user_id_provider: UserIDProviderI

    async def __call__(self, context: JoinReceiptDTO) -> None:
        user_id = self.user_id_provider.get_current_user_id()
        receipt = await self.receipt_db_gateway.fetch(id=context.receipt_id)
        receipt.append_participant(user_id)

        async with self.transaction_manager:
            await self.receipt_db_gateway.save(receipt)
