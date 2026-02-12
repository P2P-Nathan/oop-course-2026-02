"""
The WithdrawableStack class is a generic data structure implementing
logic for a stack of unique items where any given item can additionally be
removed from any part of the stack.
"""

from __future__ import annotations
from collections.abc import Hashable, Iterable
from typing import Generic, Self, TypeVar

ItemT = TypeVar("ItemT", bound=Hashable)


class WithdrawableStack(Generic[ItemT]):
    """
    A generic data structure supporting the following operations:

    - peeking at the top item of the stack
    - pushing an item on the top of the stack
    - popping an item from the top of the stack
    - counting the number of items in the stack (see __len__)
    - checking if an item is in the stack (see __contains__)
    - removeing an item from the stack, if it is in the stack

    Elements in the stack must be hashable and unique.
    Pushing raises error if the element being pushed on top of the stack
    is already present in the stack.
    """

    __contents: set[ItemT]
    """ The items currently in the stack. """
    __stack: list[ItemT]
    """
    Items in the stack, including ones which were removed but are still
    buried under some item currently in the stack.
    """

    def __new__(cls, items: Iterable[ItemT] = ()) -> Self:
        """
        Constructor for the stack. If items are passed,
        they are inserted in the order given.
        """
        self = super().__new__(cls)
        self.__contents = set()
        self.__stack = []
        for item in items:
            self.push(item)
        return self

    def peek(self) -> ItemT:
        """
        Returns the item at the top of the stack.

        :raises IndexError: if the stack is empty.
        """
        self._enforce_not_empty()
        return self.__stack[-1]

    def push(self, item: ItemT) -> None:
        """
        Pushes an item at the top of the stack.

        :raises ValueError: if the item is already in the stack.
        """
        if item in self:
            # I delegate checking that an item is in the stack to __contains__
            raise ValueError(f"Item is already in the stack: {item!r}")
        self.__stack.append(item)
        self.__contents.add(item)

    def pop(self) -> ItemT:
        """
        Pops and returns the item at the top of the stack.

        :raises IndexError: if the stack is empty.
        """
        self._enforce_not_empty()
        item = self.__stack.pop()  # stack not empty, can pop safely
        self.__contents.remove(item)  # item was in stack, can remove safely
        return item

    def remove(self, item: ItemT) -> None:
        """
        Removes an item from the stack.

        :raises KeyError: if the item was not in the stack.
        """
        try:
            self.__contents.remove(item)
        except KeyError:
            # Catch the inner error, don't expose it, and raise your error:
            raise KeyError(f"Item is not in the stack: {item!r}") from None
            # raising a different error, breaking the error chain ^^^^^^^^^

        # Example of a re-raise which keeps information about inner error:
        # try:
        #     ...
        # except KeyError as e:
        #     raise ValueError("...") from e
        #     #                       ^^^^^^ keeps track of inner error traces

    def __len__(self) -> int:
        """
        Returns the number of items in the stack.

        Automatically implements bool conversion as as self.len > 0.
        """
        return len(self.__contents)

    def __contains__(self, item: ItemT) -> bool:
        """
        Special method implementing containment test: item in stack
        """
        return item in self.__contents

    def _enforce_not_empty(self) -> None:
        """
        Protected method responsible for enforcing that the stack is not empty.

        A the end of this operation, either:

        - the stack is empty and IndexError is raised
        - the last item in self.__stack is in self.__contents

        """
        if not (contents := self.__contents):
            raise IndexError("Stack is empty.")
        stack = self.__stack
        while stack[-1] not in contents:
            stack.pop()
        # while (last := stack.pop()) not in contents:
        #     pass
        # stack.append(last)
