from __future__ import annotations

from decimal import Decimal
from typing import Self, override

from core.domain.exceptions import NegativeOrZeroAmountError

_DecimalInput = Decimal | int | str


class _PositiveDecimal:
    """Immutable positive, finite decimal value object."""

    __slots__: tuple[str] = ("_value",)

    def __init__(
        self,
        value: _DecimalInput,
        prev: Self | None = None,
    ) -> None:
        value = Decimal(value)

        if not value.is_finite() or value <= 0:
            raise NegativeOrZeroAmountError(prev, value)

        self._value: Decimal = value

    @property
    def value(self) -> Decimal:
        return self._value

    def __add__(self, other: Self) -> Self:
        self._ensure_same_type(other)
        return type(self)(self._value + other._value, prev=self)

    def __sub__(self, other: Self) -> Self:
        self._ensure_same_type(other)
        return type(self)(self._value - other._value, prev=self)

    def __mul__(self, other: _DecimalInput) -> Self:
        return type(self)(self._value * Decimal(other), prev=self)

    def __rmul__(self, other: _DecimalInput) -> Self:
        return self * other

    def __truediv__(self, other: _DecimalInput) -> Self:
        return type(self)(self._value / Decimal(other), prev=self)

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented

        return self._value == other._value

    def __lt__(self, other: Self) -> bool:
        self._ensure_same_type(other)
        return self._value < other._value

    def __le__(self, other: Self) -> bool:
        self._ensure_same_type(other)
        return self._value <= other._value

    def __gt__(self, other: Self) -> bool:
        self._ensure_same_type(other)
        return self._value > other._value

    def __ge__(self, other: Self) -> bool:
        self._ensure_same_type(other)
        return self._value >= other._value

    @override
    def __hash__(self) -> int:
        return hash((type(self), self._value))

    def __bool__(self) -> bool:
        return True

    @override
    def __str__(self) -> str:
        return str(self._value)

    @override
    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._value!r})"

    def _ensure_same_type(self, other: object) -> None:
        if type(self) is not type(other):
            raise TypeError


class Amount(_PositiveDecimal):
    """Represents a positive physical quantity."""


class Money(_PositiveDecimal):
    """Represents a positive monetary amount."""
