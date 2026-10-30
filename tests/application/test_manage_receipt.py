from typing import cast
from unittest.mock import AsyncMock, Mock, call
from uuid import uuid4

import pytest
from mimesis import Field, Fieldset

from core.application.common.agent import AgentI
from core.application.common.asr import AutomaticSpeechRecognizerI
from core.application.common.database import (
    ReceiptDBGatewayI,
    TransactionManagerI,
    UserDBGatewayI,
)
from core.application.common.ocr import OpticalCharacterRecognizerI
from core.application.receipt.manage import ManageReceipt, ManageReceiptDTO
from core.domain.exceptions import AccessDeniedError
from core.domain.models import Receipt
from core.domain.value_objects import MessageText, UserID


@pytest.fixture
def asr() -> AutomaticSpeechRecognizerI:
    asr_mock = Mock()
    asr_mock.recognize_text = AsyncMock()
    return asr_mock


@pytest.fixture
def ocr() -> OpticalCharacterRecognizerI:
    ocr_mock = Mock()
    ocr_mock.recognize_text = AsyncMock()
    return ocr_mock


@pytest.fixture
def agent() -> AgentI:
    agent_mock = Mock()
    agent_mock.invoke = AsyncMock()
    return agent_mock


@pytest.fixture
def receipt_db_gateway(receipt: Receipt) -> ReceiptDBGatewayI:
    receipt_db_gateway_mock = Mock()
    receipt_db_gateway_mock.fetch = AsyncMock(return_value=receipt)
    receipt_db_gateway_mock.save = AsyncMock()
    return receipt_db_gateway_mock


@pytest.fixture
def user_db_gateway() -> UserDBGatewayI:
    user_db_gateway_mock = Mock()
    user_db_gateway_mock.fetch_many = AsyncMock()
    return user_db_gateway_mock


@pytest.fixture
def input_dto(receipt: Receipt) -> ManageReceiptDTO:
    field = Field()
    fieldset = Fieldset()

    return ManageReceiptDTO(
        receipt_id=receipt.id,
        text=MessageText(field("sentence")),
        photos=tuple(
            fieldset("image", i=field("integer_number", start=1, end=10))
        ),
        audios=tuple(
            fieldset("audio", i=field("integer_number", start=1, end=10))
        ),
    )


async def test_manage_receipt_called_by_participant(
    receipt: Receipt,
    asr: AutomaticSpeechRecognizerI,
    ocr: OpticalCharacterRecognizerI,
    agent: AgentI,
    transaction_manager: TransactionManagerI,
    receipt_db_gateway: ReceiptDBGatewayI,
    user_db_gateway: UserDBGatewayI,
    input_dto: ManageReceiptDTO,
) -> None:
    user_id = next(iter(receipt.participant_ids))
    user_id_provider_mock = Mock()
    user_id_provider_mock.get_current_user_id = Mock(return_value=user_id)

    ensure_access_service_mock = Mock()

    interactor = ManageReceipt(
        asr=asr,
        ocr=ocr,
        ensure_access_service=ensure_access_service_mock,
        agent=agent,
        transaction_manager=transaction_manager,
        receipt_db_gateway=receipt_db_gateway,
        user_db_gateway=user_db_gateway,
        user_id_provider=user_id_provider_mock,
    )

    res = await interactor(input_dto)

    asr_mock = cast(AsyncMock, asr.recognize_text)
    ocr_mock = cast(AsyncMock, ocr.recognize_text)

    assert res.message
    asr_mock.assert_has_awaits([call(audio) for audio in input_dto.audios])
    assert asr_mock.await_count == len(input_dto.audios)
    ocr_mock.assert_has_awaits([call(photo) for photo in input_dto.photos])
    assert ocr_mock.await_count == len(input_dto.photos)


async def test_manage_receipt_called_by_not_participant(
    receipt: Receipt,
    asr: AutomaticSpeechRecognizerI,
    ocr: OpticalCharacterRecognizerI,
    agent: AgentI,
    transaction_manager: TransactionManagerI,
    receipt_db_gateway: ReceiptDBGatewayI,
    user_db_gateway: UserDBGatewayI,
    input_dto: ManageReceiptDTO,
) -> None:
    user_id = UserID(uuid4())
    user_id_provider_mock = Mock()
    user_id_provider_mock.get_current_user_id = Mock(return_value=user_id)

    ensure_access_service_mock = Mock(side_effect=AccessDeniedError)

    interactor = ManageReceipt(
        asr=asr,
        ocr=ocr,
        ensure_access_service=ensure_access_service_mock,
        agent=agent,
        transaction_manager=transaction_manager,
        receipt_db_gateway=receipt_db_gateway,
        user_db_gateway=user_db_gateway,
        user_id_provider=user_id_provider_mock,
    )

    with pytest.raises(AccessDeniedError):
        await interactor(input_dto)
