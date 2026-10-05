from unittest.mock import AsyncMock, MagicMock, Mock

import pytest
from mimesis import Field

from core.application.common.database import (
    ExternalIDAlreadyExistsError,
    TransactionManagerI,
    UserDBGatewayI,
)
from core.application.common.external_id_provider import ExternalIDProviderI
from core.application.users.register import RegisterUser, RegisterUserDTO
from core.domain.models import RealUser
from core.domain.services import CreateRealUser
from tests.mocks import UserData


@pytest.fixture
def create_user_service(real_user: RealUser) -> CreateRealUser:
    return MagicMock(return_value=real_user)


@pytest.fixture
def user_db_gateway() -> UserDBGatewayI:
    user_db_gateway_mock = Mock()
    user_db_gateway_mock.save = AsyncMock()
    return user_db_gateway_mock


@pytest.fixture
def external_id_provider() -> ExternalIDProviderI:
    _ = Field()
    external_id_provider_mock = Mock()
    external_id_provider_mock.get_current_user_external_id = AsyncMock(
        return_value=_("uuid")
    )
    return external_id_provider_mock


async def test_register_new_user(
    user_data: UserData,
    create_user_service: MagicMock,
    transaction_manager: TransactionManagerI,
    user_db_gateway: UserDBGatewayI,
    external_id_provider: ExternalIDProviderI,
) -> None:
    external_id_db_gateway = Mock()
    external_id_db_gateway.save = AsyncMock()

    interactor = RegisterUser(
        create_user_service=create_user_service,
        transaction_manager=transaction_manager,
        user_db_gateway=user_db_gateway,
        external_id_db_gateway=external_id_db_gateway,
        external_id_provider=external_id_provider,
    )

    res = await interactor(RegisterUserDTO(nickname=user_data["nickname"]))

    assert res
    create_user_service.assert_called_once_with(user_data["nickname"])


async def test_register_already_existed_user(
    user_data: UserData,
    create_user_service: MagicMock,
    transaction_manager: TransactionManagerI,
    user_db_gateway: UserDBGatewayI,
    external_id_provider: ExternalIDProviderI,
) -> None:
    external_id_db_gateway = Mock()
    external_id_db_gateway.save = AsyncMock(
        side_effect=ExternalIDAlreadyExistsError
    )

    interactor = RegisterUser(
        create_user_service=create_user_service,
        transaction_manager=transaction_manager,
        user_db_gateway=user_db_gateway,
        external_id_db_gateway=external_id_db_gateway,
        external_id_provider=external_id_provider,
    )

    with pytest.raises(ExternalIDAlreadyExistsError):
        await interactor(RegisterUserDTO(nickname=user_data["nickname"]))
