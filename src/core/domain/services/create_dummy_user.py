from uuid import uuid7

from core.domain.models.user import DummyUser
from core.domain.value_objects import UserID, UserNickname


class CreateDummyUser:
    def __call__(self, nickname: UserNickname) -> DummyUser:
        return DummyUser(id=UserID(uuid7()), nickname=nickname)
