from types import TracebackType
from typing import Self

import pytest

from core.application.common.database import TransactionManagerI


class FakeTransactionManager(TransactionManagerI):
    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if exc_value is not None:
            raise exc_value


@pytest.fixture
def transaction_manager() -> TransactionManagerI:
    return FakeTransactionManager()
