
from typing import Self


class Seller:
    """A seller in a marketplace."""
    _name: str

    def __new__(cls, name: str) -> Self:
        self = object.__new__(cls)
        self._name = name
        return self
