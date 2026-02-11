"""This is the implementation of the stack from the excercise"""
from typing import Hashable, Self


class WithdrawableStack[T: Hashable]:


    _stack: list[T]

    def __new__(cls) -> Self:
        self = object.__new__(cls)
        self._stack = []
        return self
    
    # Instance methods
    def peek(self) -> T:
        if(not self._stack):
            raise IndexError("Stack is empty")
        if(len(self._stack) == 0):
            raise IndexError("Stack has only no elements")
        return self._stack[-1]
    
    def push(self, item: T) -> None:
        # Check for duplicates
        if item in self._stack:
            raise ValueError(f"Item {item} already exists in stack")
        self._stack.append(item)

    def pop(self) -> T:
        if(not self._stack):
            raise IndexError("Stack is empty")
        return self._stack.pop()
    
    def remove(self, item: T) -> None:
        if(not self._stack):
            raise IndexError("Stack is empty")
        try:
            self._stack.remove(item)
        except ValueError:
            raise ValueError(f"Item {item} not found in stack")
        
    def __len__(self) -> int:
        return len(self._stack)
    
    def __contains__(self, item: T) -> bool:
        return item in self._stack