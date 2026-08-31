from abc import abstractmethod
from typing import NewType, Protocol

from core.domain.value_objects.types import Photo

RecognizedImageText = NewType("RecognizedImageText", str)


class OpticalCharacterRecognizerI(Protocol):
    @abstractmethod
    async def recognize_text(self, photo: Photo) -> RecognizedImageText:
        raise NotImplementedError
