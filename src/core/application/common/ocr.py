from typing import NewType, Protocol

from core.domain.value_objects.types import Photo

ImageText = NewType("ImageText", str)


class OpticalCharacterRecognizerI(Protocol):
    async def recognize_text(self, photo: Photo) -> ImageText: ...
