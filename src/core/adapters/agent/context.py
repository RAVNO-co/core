from typing import TypedDict

from core.domain.models.user import User
from core.domain.value_objects import UserID


class ReceiptModificationContext(TypedDict):
    user_id_mapping: dict[UserID, User]
