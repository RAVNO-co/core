import asyncio
from dataclasses import dataclass
from typing import final

from core.application.common import Interactor
from core.application.common.agent import AgentI, AgentMessage, HumanRequest
from core.application.common.asr import AutomaticSpeechRecognizerI, SpeechText
from core.application.common.database import (
    ReceiptDBGatewayI,
    TransactionManagerI,
)
from core.application.common.ocr import ImageText, OpticalCharacterRecognizerI
from core.application.common.user_id_provider import UserIDProviderI
from core.domain.services import EnsureAccess
from core.domain.value_objects import MessageText, ReceiptID
from core.domain.value_objects.types import Audio, Photo


@dataclass(frozen=True, slots=True)
class ManageReceiptDTO:
    receipt_id: ReceiptID
    text: MessageText | None
    photos: tuple[Photo, ...]
    audios: tuple[Audio, ...]


@dataclass(frozen=True, slots=True)
class ManageReceiptResultDTO:
    message: AgentMessage


@final
@dataclass(frozen=True, slots=True)
class ManageReceipt(Interactor[ManageReceiptDTO, ManageReceiptResultDTO]):
    asr: AutomaticSpeechRecognizerI
    ocr: OpticalCharacterRecognizerI
    ensure_access_service: EnsureAccess
    agent: AgentI
    transaction_manager: TransactionManagerI
    receipt_db_gateway: ReceiptDBGatewayI
    user_id_provider: UserIDProviderI

    async def __call__(
        self, context: ManageReceiptDTO
    ) -> ManageReceiptResultDTO:
        user_id = self.user_id_provider.get_current_user_id()
        receipt = await self.receipt_db_gateway.fetch(id=context.receipt_id)

        self.ensure_access_service(receipt, user_id)

        response = await self.agent.invoke(
            HumanRequest(
                user_id,
                context.text,
                *await self.transcribe_media(context.audios, context.photos),
            ),
            receipt,
        )

        async with self.transaction_manager:
            await self.receipt_db_gateway.save(response.updated_receipt)

        return ManageReceiptResultDTO(response.answer)

    async def transcribe_media(
        self, audios: tuple[Audio, ...], photos: tuple[Photo, ...]
    ) -> tuple[list[SpeechText], list[ImageText]]:
        """Send audio and image recognition requests concurrently to reduce latency."""
        audio_future = asyncio.gather(
            *(self.asr.recognize_text(audio) for audio in audios)
        )
        photo_future = asyncio.gather(
            *(self.ocr.recognize_text(photo) for photo in photos)
        )
        return await asyncio.gather(audio_future, photo_future)
