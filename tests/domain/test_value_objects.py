from random import randint

import pytest

from core.domain.exceptions import NegativeOrZeroAmountError
from core.domain.value_objects import Amount, Money


def test_negative_amount_error():
    with pytest.raises(NegativeOrZeroAmountError):
        Amount(randint(-5, 0))  # ruff: ignore[suspicious-non-cryptographic-random-usage]


def test_negative_money_error():
    with pytest.raises(NegativeOrZeroAmountError):
        Money(randint(-5, 0))  # ruff: ignore[suspicious-non-cryptographic-random-usage]
