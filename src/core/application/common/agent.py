from abc import abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass
from typing import NewType, Protocol

from core.application.common.asr import RecognizedSpeechText
from core.application.common.ocr import RecognizedImageText
from core.domain.models import Receipt, User
from core.domain.value_objects import MessageText, UserID


@dataclass(slots=True, frozen=True)
class HumanRequest:
    user_id: UserID
    users_input: MessageText | None
    transcribed_audios: Iterable[RecognizedSpeechText]
    transcribed_photos: Iterable[RecognizedImageText]


AgentMessage = NewType("AgentMessage", str)


@dataclass(slots=True, frozen=True)
class AgentResponse:
    answer: AgentMessage
    updated_receipt: Receipt


class AgentI(Protocol):
    @abstractmethod
    async def invoke(
        self, request: HumanRequest, receipt: Receipt, participants: list[User]
    ) -> AgentResponse:
        raise NotImplementedError
