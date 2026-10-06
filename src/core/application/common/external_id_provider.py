from typing import Protocol

from core.domain.value_objects import ExternalID


class ExternalIDProviderI(Protocol):
    async def get_current_user_external_id(self) -> ExternalID: ...
