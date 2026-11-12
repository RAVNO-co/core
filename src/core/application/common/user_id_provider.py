from typing import Protocol

from core.domain.value_objects import UserID


class UserIDProviderI(Protocol):
    def get_current_user_id(self) -> UserID:
        """Obtain the current user's identity.
        Gets populated on presentation layer

        Raises:
            UserIDNotProvidedError: user request have not provided indentity
        """
        ...


class UserIDNotProvidedError(Exception): ...
