from collections.abc import Iterable
from dataclasses import dataclass
from typing import NewType, Protocol

from core.application.common.asr import SpeechText
from core.application.common.ocr import ImageText
from core.domain.models import Receipt, User
from core.domain.value_objects import MessageText, UserID


@dataclass(slots=True, frozen=True)
class HumanRequest:
    user_id: UserID
    message_text: MessageText | None
    transcribed_audios: Iterable[SpeechText]
    transcribed_photos: Iterable[ImageText]


AgentMessage = NewType("AgentMessage", str)


@dataclass(slots=True, frozen=True)
class AgentResponse:
    answer: AgentMessage
    updated_receipt: Receipt


class AgentI(Protocol):
    async def invoke(
        self, request: HumanRequest, receipt: Receipt, participants: list[User]
    ) -> AgentResponse: ...
