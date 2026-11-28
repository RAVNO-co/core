from unittest.mock import AsyncMock, Mock

import pytest

from core.application.common.database.receipt_gateway import (
    ReceiptDBGatewayI,
)
from core.application.common.database.user_gateway import UserDBGatewayI
from core.application.receipt.list import ListReceipt, ListReceiptDTO
from core.domain.models.receipt import Receipt


@pytest.fixture
def receipt_db_gateway(receipt: Receipt) -> ReceiptDBGatewayI:
    receipt_db_gateway_mock = Mock()
    receipt_db_gateway_mock.fetch_many = AsyncMock(return_value=[receipt])
    return receipt_db_gateway_mock


@pytest.fixture
def user_db_gateway() -> UserDBGatewayI:
    user_db_gateway_mock = Mock()
    user_db_gateway_mock.fetch_many = AsyncMock()
    user_db_gateway_mock.bulk_save = AsyncMock()
    return user_db_gateway_mock


@pytest.fixture
def input_dto(receipt: Receipt) -> ListReceiptDTO:

    return ListReceiptDTO(cursor=receipt.id)


async def test_list_normal(
    receipt: Receipt,
    receipt_db_gateway: ReceiptDBGatewayI,
    user_db_gateway: UserDBGatewayI,
    input_dto: ListReceiptDTO,
) -> None:

    user_id = next(iter(receipt.participant_ids))
    user_id_provider_mock = Mock()
    user_id_provider_mock.get_current_user_id = Mock(return_value=user_id)
    interactor = ListReceipt(
        receipt_db_gateway=receipt_db_gateway,
        user_db_gateway=user_db_gateway,
        user_id_provider=user_id_provider_mock,
    )
    res = await interactor(input_dto)
    assert len(res.receipts) == 1
    assert res.receipts[0].id == receipt.id
