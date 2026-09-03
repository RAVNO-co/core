from dataclasses import dataclass

from core.domain.value_objects import (
    UserID,
    UserNickname,
)


@dataclass
class _BaseUser:
    id: UserID
    nickname: UserNickname


@dataclass
class DummyUser(_BaseUser): ...


@dataclass
class RealUser(_BaseUser): ...


User = DummyUser | RealUser
