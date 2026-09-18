from dataclasses import dataclass
from typing import final

from core.application.common import Interactor
from core.application.common.database.integration_gateway import (
    IntegrationDBGatewayI,
)
from core.application.common.database.transaction_manager import (
    TransactionManagerI,
)
from core.application.common.database.user_gateway import UserDBGatewayI
from core.domain.services import CreateRealUser
from core.domain.value_objects import UserID, UserNickname
from core.domain.value_objects.types import IntegrationID, IntegrationType


@dataclass
class RegisterUserDTO:
    integration_type: IntegrationType
    integration_id: IntegrationID
    nickname: UserNickname


@final
@dataclass(frozen=True)
class RegisterUser(Interactor[RegisterUserDTO, UserID]):
    create_user_service: CreateRealUser
    transaction_manager: TransactionManagerI
    user_db_gateway: UserDBGatewayI
    integration_db_gateway: IntegrationDBGatewayI

    async def __call__(self, context: RegisterUserDTO) -> UserID:
        user = self.create_user_service(context.nickname)

        async with self.transaction_manager:
            await self.user_db_gateway.save(user)
            await self.integration_db_gateway.save(
                user.id, context.integration_id, context.integration_type
            )

        return user.id

IntegrationAlreadyExists
