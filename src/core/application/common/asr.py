from typing import NewType, Protocol

from core.domain.value_objects.types import Audio

SpeechText = NewType("SpeechText", str)


class AutomaticSpeechRecognizerI(Protocol):
    async def recognize_text(self, audio: Audio) -> SpeechText: ...
