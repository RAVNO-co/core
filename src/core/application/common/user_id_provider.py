from typing import Protocol

from core.domain.value_objects import UserID


class UserIDProviderI(Protocol):
    def get_current_user_id(self) -> UserID:
        """User identitiy obtainer
        Gets populated on presentation layer

        Raises:
            UserIDNotProvidedError: user request have not provided indentity
        """
        ...


class UserIDNotProvidedError(Exception): ...
