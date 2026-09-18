from typing import Protocol

from core.domain.value_objects import UserID
from core.domain.value_objects.types import IntegrationID, IntegrationType


class IntegrationDBGatewayI(Protocol):
    async def fetch_user_id(
        self,
        /,
        integration_id: IntegrationID,
        integration_type: IntegrationType,
    ) -> UserID: ...

    async def save(
        self,
        /,
        user_id: UserID,
        integration_id: IntegrationID,
        integration_type: IntegrationType,
    ) -> None: ...
