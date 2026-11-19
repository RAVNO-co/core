from random import randint

import pytest
from mimesis import Text

from core.application.common.agent import HumanRequest
from core.application.common.asr import SpeechText
from core.application.common.ocr import ImageText
from core.domain.models import Receipt
from core.domain.value_objects import MessageText
from tests.mocks import RealUserFactory


@pytest.fixture
def human_request(
    receipt: Receipt, real_user_factory: RealUserFactory
) -> HumanRequest:
    text_provider = Text()
    return HumanRequest(
        user_id=next(iter(receipt.participant_ids)),
        message_text=MessageText(text_provider.text()),
        transcribed_audios=tuple(
            SpeechText(text_provider.text()) for _ in range(randint(0, 10))
        ),
        transcribed_photos=tuple(
            ImageText(text_provider.text()) for _ in range(randint(0, 10))
        ),
        receipt=receipt,
        participants=[
            real_user_factory(id=user_id)
            for user_id in receipt.participant_ids
        ],
    )
