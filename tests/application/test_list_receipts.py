from collections.abc import Sequence
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
def receipt_db_gateway(receipts: Sequence[Receipt]) -> ReceiptDBGatewayI:
    receipt_db_gateway_mock = Mock()
    receipt_db_gateway_mock.fetch_page = AsyncMock(return_value=receipts)
    return receipt_db_gateway_mock


@pytest.fixture
def user_db_gateway() -> UserDBGatewayI:
    user_db_gateway_mock = Mock()
    user_db_gateway_mock.fetch_many = AsyncMock()
    user_db_gateway_mock.bulk_save = AsyncMock()
    return user_db_gateway_mock

async def test_list_normal() -> None: ...
async def test_list_by_unathenthiated_user() -> None: ...
async def test_list_by_no_receipt_user() -> None: ...
async def test_list_by_nonexistent_user() -> None: ...
async def test_list_cursor_not_in_list() -> None: ...
