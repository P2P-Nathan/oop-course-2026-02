"""
Example implementation on bag structure
"""

from collections.abc import Hashable, Iterable, Iterator
from typing import Self


class Bag[T: Hashable]:
    """A bag is an unordered collection of items with duplicates allowed"""

    __counts: dict[T, int]
    """ Count of items in the bag, always positive"""

    def __new__(cls, items: Iterable[T]) -> Self:
        self = object.__new__(cls)
        self.__counts = {}
        self.extend(items)
        return self

    # Bag operations
    def add(self, item: T) -> None:
        """Add an item to our bag"""
        self.__counts[item] = self.count(item) + 1
    
    def extend(self, items: Iterable[T]) -> None:
        """Add iterables to our itme"""
        for i in items:
            self.add(i)

    def count(self, item: T) -> int:
        """Count of items"""
        return self.__counts.get(item, 0)



    # Dunder methods

    def __iter__(self) -> Iterator[T]:
        """Iterate through the bag"""
        # Yield allows to resume from the same point.  Uses a GENERATOR pattern to create the iterator
        for item, count in self.__counts.items():
            for _ in range(count):
                yield item
    
    def __len__(self) -> int:
        """Get the length of our bag"""
        return sum(self.__counts.values())

    def __contains__(self, item: T) -> bool:
        """Check if something is in the bag, implements in operator"""
        return item in self.__counts