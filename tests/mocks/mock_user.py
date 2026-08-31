from typing import Protocol, TypedDict, Unpack

import pytest
from mimesis import Field, Schema

from core.domain.models.user import DummyUser, RealUser
from core.domain.services import create_dummy_user, create_real_user
from core.domain.value_objects.types import UserID, UserNickname


class UserData(TypedDict, total=False):
    id: UserID
    nickname: UserNickname


class UserDataFactory(Protocol):
    def __call__(self, **fields: Unpack[UserData]) -> UserData: ...


class RealUserFactory(Protocol):
    def __call__(self, **fields: Unpack[UserData]) -> RealUser: ...


class DummyUserFactory(Protocol):
    def __call__(self, **fields: Unpack[UserData]) -> DummyUser: ...


@pytest.fixture
def user_data_factory() -> UserDataFactory:
    def factory(**fields: Unpack[UserData]) -> UserData:
        field = Field()
        schema = Schema(
            lambda: {"id": field("uuid"), "nickname": field("name")},
            iterations=1,
        )
        return {**schema.create()[0], **fields}  # type:ignore[typeddict-item]

    return factory


@pytest.fixture
def user_data(user_data_factory: UserDataFactory) -> UserData:
    return user_data_factory()


@pytest.fixture
def real_user_factory(user_data_factory: UserDataFactory) -> RealUserFactory:
    def factory(**fields: Unpack[UserData]) -> RealUser:
        fields = user_data_factory(**fields)
        user = create_real_user(fields["nickname"])
        user.id = fields.get("id", user.id)
        return user

    return factory


@pytest.fixture
def real_user(real_user_factory: RealUserFactory) -> RealUser:
    return real_user_factory()


@pytest.fixture
def dummy_user_factory(user_data_factory: UserDataFactory) -> DummyUserFactory:
    def factory(**fields: Unpack[UserData]) -> DummyUser:
        fields = user_data_factory(**fields)
        user = create_dummy_user(fields["nickname"])
        user.id = fields.get("id", user.id)
        return user

    return factory


@pytest.fixture
def dummy_user(dummy_user_factory: DummyUserFactory) -> DummyUser:
    return dummy_user_factory()
