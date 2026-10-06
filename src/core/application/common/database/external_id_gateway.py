from typing import Protocol

from core.domain.value_objects import ExternalID, UserID


class ExternalIDDBGatewayI(Protocol):
    async def fetch_user_id(
        self,
        external_id: ExternalID,
    ) -> UserID:
        """Find user by third-party id
        Raises:
            ExternalIDNotFoundError: third-party id was not found
        """
        ...

    async def save(
        self,
        user_id: UserID,
        external_id: ExternalID,
    ) -> None:
        """Saves user's third-party id
        Raises:
            ExternalIDAlreadyExistsError: Such provider and external_id pair
                already exists
        """
        ...


class ExternalIDNotFoundError(Exception): ...


class ExternalIDAlreadyExistsError(Exception): ...
