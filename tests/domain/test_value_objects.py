from random import randint

import pytest

from core.domain.exceptions import NegativeOrZeroAmountError
from core.domain.value_objects import Amount, Money


def test_negative_amount_error() -> None:
    with pytest.raises(NegativeOrZeroAmountError):
        Amount(randint(-5, 0))


def test_negative_money_error() -> None:
    with pytest.raises(NegativeOrZeroAmountError):
        Money(randint(-5, 0))
