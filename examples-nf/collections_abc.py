"""
Reproduces the a fragment of stdlib
"""

# Not straightforrward to find the sources as its from _collections_abc
# import _collections_abc
# old source, not great
# class Iterable(metaclass=ABCMeta):

#     __slots__ = ()

#     @abstractmethod
#     def __iter__(self):
#         while False:
#             yield None

#     @classmethod
#     def __subclasshook__(cls, C):
#         if cls is Iterable:
#             return _check_methods(C, "__iter__")
#         return NotImplemented

#     __class_getitem__ = classmethod(GenericAlias)

from typing import Callable, Protocol, runtime_checkable

# Protocols are the spiritual equivalent of equivalent to interfaces in other languages.  They are a way to specify a set of methods that a class must implement, without specifying how those methods should be implemented.  They are also used to specify the expected behavior of a class, without specifying the implementation details.

@runtime_checkable
class Iterator[T](Protocol):
    __slots__ = ()
    def __next__(self) -> T: 
        """Return the next item from the iterator.  If there are no more items, raise StopIteration."""
        

@runtime_checkable
class Iterable[T](Protocol):
    __slots__ = ()
    def __iter__(self) -> Iterator[T]: 
        """Return an iterator over the items in the iterable."""

@runtime_checkable
class Sized(Protocol):
    __slots__ = ()
    def __len__(self) -> int: 
        """Return the number of items in the container."""

@runtime_checkable
class Container[T](Protocol):
    __slots__ = ()
    def __contains__(self, item: T) -> bool: 
        """Return True if the container contains the item, False otherwise."""


# This is an example of iterface segregation and dependency inversion
def iter_map(iterable: Iterable[S], func: Callable[[S], T]) -> Iterable[T]:
    """Return an iterator that applies func to every item of iterable, yielding the results."""
    for item in iterable:
        yield func(item)


@runtime_checkable
class MutableContainer[T](Container[T], Protocol):
    __slots__ = ()
    def add(self, item: T) -> None: 
        """
        Add an item to the container.
        
        Invariant: after calling add(item), item is in the container.
        """
    
    def remove(self, item: T) -> None: 
        """
        Remove an item from the container.
        
        Invariant: after calling remove(item), item my be in a container if multiplicity is allowed
        """

    def clear(self, item: T) -> None:
        """
        Remove all items from the container.
        
        Invariant: after calling clear(), the container is empty.
        """

class IndexOfMixIn[T](Iterable[T]):
    __slots__ = ()
    def index_of(self, value: T, start: int = 0, stop: int | None = None) -> int:
        """Return the index of the first occurrence of item in the container.  If item is not found, raise ValueError."""
        
        index = 0
        for item_ in self:
            if index < start:
                index += 1
                continue
            if stop is not None and index >= stop:
                break
            if item_ == value:
                return index
            index += 1
        raise ValueError(f"{value} is not in container")
    