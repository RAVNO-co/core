from unittest.mock import AsyncMock, Mock
from uuid import uuid4

import pytest

from core.application.common.database.receipt_gateway import ReceiptDBGatewayI
from core.application.common.database.transaction_manager import (
    TransactionManagerI,
)
from core.application.common.database.user_gateway import UserDBGatewayI
from core.application.receipt.join import JoinReceipt, JoinReceiptDTO
from core.domain.models.receipt import Receipt
from core.domain.value_objects.types import UserID


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
    user_db_gateway_mock.bulk_save = AsyncMock()
    return user_db_gateway_mock


async def test_joining_receipt_by_participant(
    transaction_manager: TransactionManagerI,
    receipt_db_gateway: ReceiptDBGatewayI,
    user_db_gateway: UserDBGatewayI,
    receipt: Receipt,
) -> None:
    user_id = next(iter(receipt.participant_ids))
    user_id_provider_mock = Mock()
    user_id_provider_mock.get_current_user_id = Mock(return_value=user_id)

    interactor = JoinReceipt(
        transaction_manager=transaction_manager,
        receipt_db_gateway=receipt_db_gateway,
        user_db_gateway=user_db_gateway,
        user_id_provider=user_id_provider_mock,
    )
    await interactor(JoinReceiptDTO(receipt.id))
    assert user_id in receipt.participant_ids


async def test_joining_receipt_by_non_participant(
    transaction_manager: TransactionManagerI,
    receipt_db_gateway: ReceiptDBGatewayI,
    user_db_gateway: UserDBGatewayI,
    receipt: Receipt,
) -> None:
    user_id = UserID(uuid4())
    user_id_provider_mock = Mock()
    user_id_provider_mock.get_current_user_id = Mock(return_value=user_id)

    interactor = JoinReceipt(
        transaction_manager=transaction_manager,
        receipt_db_gateway=receipt_db_gateway,
        user_db_gateway=user_db_gateway,
        user_id_provider=user_id_provider_mock,
    )
    await interactor(JoinReceiptDTO(receipt.id))
    assert user_id in receipt.participant_ids
