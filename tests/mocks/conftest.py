import pytest
from mimesis import Field


@pytest.fixture(scope="session")
def mimesis_field() -> Field:
    return Field()
