from collections.abc import Sequence
from typing import Protocol, TypedDict, Unpack

from core.domain.models import User
from core.domain.value_objects import UserID


class UserFilters(TypedDict, total=False):
    id: UserID


class MultipleUsersFilters(TypedDict, total=False):
    ids: Sequence[UserID]


class UserDBGatewayI(Protocol):
    async def fetch(self, **filters: Unpack[UserFilters]) -> User:
        """Find user that satisfies all **filters
        Raises:
            UserNotFoundError: third-party id was not found
        """
        ...

    async def fetch_many(
        self, **filters: Unpack[MultipleUsersFilters]
    ) -> tuple[User, ...]: ...
    async def save(self, user: User) -> None: ...


class UserNotFoundError(Exception): ...
