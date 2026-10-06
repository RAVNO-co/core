from dataclasses import dataclass
from enum import StrEnum
from typing import NewType
from uuid import UUID

ExternalUserID = NewType("ExternalUserID", UUID)


class IntegrationProvider(StrEnum):
    MAX = "max"
    TELEGRAM = "telegram"


@dataclass(frozen=True, slots=True)
class ExternalID:
    """User id in third-party app"""

    id: ExternalUserID
    provider: IntegrationProvider
