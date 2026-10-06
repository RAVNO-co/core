from dataclasses import dataclass
from typing import final

from core.application.common import Interactor
from core.application.common.database import (
    ExternalIDDBGatewayI,
    TransactionManagerI,
    UserDBGatewayI,
)
from core.application.common.external_id_provider import ExternalIDProviderI
from core.domain.services import CreateRealUser
from core.domain.value_objects import (
    UserID,
    UserNickname,
)


@dataclass
class RegisterUserDTO:
    nickname: UserNickname


@final
@dataclass(frozen=True)
class RegisterUser(Interactor[RegisterUserDTO, UserID]):
    create_user_service: CreateRealUser
    transaction_manager: TransactionManagerI
    user_db_gateway: UserDBGatewayI
    external_id_db_gateway: ExternalIDDBGatewayI
    external_id_provider: ExternalIDProviderI

    async def __call__(self, context: RegisterUserDTO) -> UserID:
        user = self.create_user_service(context.nickname)
        external_id = (
            await self.external_id_provider.get_current_user_external_id()
        )

        async with self.transaction_manager:
            await self.user_db_gateway.save(user)
            await self.external_id_db_gateway.save(
                user.id,
                external_id,
            )

        return user.id
