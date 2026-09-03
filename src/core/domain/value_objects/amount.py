from abc import ABC
from decimal import Decimal
from typing import Self, override

from core.domain.exceptions import NegativeOrZeroAmountError

_NewDecimal = Decimal | float | str
_Decimal = Decimal | int


class _AmountABC(Decimal, ABC):
    """Represents existing amount of smth

    Rewrites returned Decimal types
    Cant be less or equal 0
    """

    def __new__(
        cls,
        value: _NewDecimal,
        prev: Self | None = None,
    ) -> Self:
        value = Decimal(value)
        if value <= 0 and value.is_finite():
            raise NegativeOrZeroAmountError(prev, value)
        return super().__new__(cls, value)

    @override
    def __add__(self, value: Decimal | int, /) -> Self:
        return self.__new__(self.__class__, super().__add__(value))

    @override
    def __mul__(self, value: _Decimal, /) -> Self:
        return self.__new__(self.__class__, super().__mul__(value))

    @override
    def __sub__(self, value: _Decimal, /) -> Self:
        return self.__new__(self.__class__, super().__sub__(value))

    def __iadd__(self, other: _Decimal, /) -> Self:
        return self.__add__(other)

    def __isub__(self, other: _Decimal, /) -> Self:
        return self.__sub__(other)


class Amount(_AmountABC):
    """Represents physical amount of smth both in quantitity and weight"""


class Money(_AmountABC):
    """Represents some amount of currency"""
