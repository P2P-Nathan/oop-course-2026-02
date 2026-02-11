"""
Implementation of a mock buffer framework to show multi-inheritance and composition. This is not a real buffer framework, but it shows how to use multiple inheritance and composition to create a flexible and extensible design.

"""

from collections import deque
from typing import Protocol, Self, overload

class Buffer(Protocol):
    """
    A buffer interface with index and slice access. 
    """

    @overload
    def __getitem__(self, idx: int) -> bytes: ...
    @overload
    def __getitem__(self, idx: slice[int, int, None]) -> bytes: ...

    def __getitem__(self, idx: int | slice) -> bytes:
        """
        Return the byte(s) at the given index or slice.
        
        Slice must be contiguous
        """
        ...

    def __len__(self) -> int:
        """
        Return the number of bytes in the buffer.
        """
        ...

class Reader:
    """
    Reads sequentially
    """

    # Subclasses will need to implement these protected attributes and methods, thats why they are protected and not private.  
    _bytes: bytearray # protected attribute to store the data
    _pos: int # protected attribute to store the current position in the data

    def __new__(cls, buf: bytearray) -> Self:
        self =  object.__new__(cls)
        self._bytes = buf
        self._pos = 0
        return self
    
    @property
    def available(self) -> int:
        """Return the number of bytes available to read."""
        return len(self._bytes) - self._pos

    def read(self, n: int) -> bytes:
        """Read n bytes from the reader and return them as bytes."""
        num_bytes = min(n, len(self._bytes) - self._pos)
        data = self._bytes[self._pos:self._pos + num_bytes]
        self._pos += num_bytes
        return data

class Writer:
    """
    Writes sequentially
    """

class BufferedWriter(Writer):
    """
    A buffered writer that writes to a writer and buffers the data.
    """


class BufferedReader(Reader):
    """
    A buffered reader that reads from a reader and buffers the data.
    """

    # Private details for this class, private is key for our name mangling and multiple subclasses
    __chunk_size: int
    __buffer: deque[int]  # for concept, not efficient for real implementation

    def read(self, num_bytes: int) -> bytes:
        """Read num_bytes from the buffered reader and return them as bytes."""
        buffer = self.__buffer
        return bytes(buffer.popleft() for _ in range(min(num_bytes, len(buffer))))

    def __read_chunk(self) -> None:
        """Read a chunk of data from the underlying reader and add it to the buffer."""
        chunk = super().read(self.__chunk_size)

        # could also be Reader.read(self, self.__chunk_size) to avoid the super() call, but this is more explicit and clear.  Also, super() is more flexible if we want to change the inheritance hierarchy later.
        self.__buffer.extend(chunk)


class RandomReader(Reader):
    """
    A random reader that reads from a reader and allows random access to the data.
    """

class RandomWriter(Writer):
    """
    A random writer that writes to a writer and allows random access to the data.
    """

class Accessor(Reader, Writer):
    """
    An accessor that can read and write sequentially.
    """

class RandomAccessor(Accessor, RandomReader, RandomWriter):
    """
    A random accessor with seeking capabilities that can be used by both readers and writers.
    """

class BufferedRandomAccessor(RandomAccessor, BufferedReader, BufferedWriter):
    """
    A buffered random accessor that combines the functionality of a buffered reader/writer and a random accessor.
    """