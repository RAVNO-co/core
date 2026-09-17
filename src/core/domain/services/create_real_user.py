from uuid import uuid7

from core.domain.models.user import RealUser
from core.domain.value_objects import UserID, UserNickname


class CreateRealUser:
    def __call__(self, nickname: UserNickname) -> RealUser:
        return RealUser(id=UserID(uuid7()), nickname=nickname)
