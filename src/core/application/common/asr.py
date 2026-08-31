from abc import abstractmethod
from typing import NewType, Protocol

from core.domain.value_objects.types import Audio

RecognizedSpeechText = NewType("RecognizedSpeechText", str)


class SpeechRecognizerI(Protocol):
    @abstractmethod
    async def recognize_text(self, audio: Audio) -> RecognizedSpeechText:
        raise NotImplementedError
