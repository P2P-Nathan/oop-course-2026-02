"""
Implementation of a mock time server connection to use in place of the builtin
:meth:`datetime.datetime.now` method, so that current time can be customised
when the library is being tested.
"""

from __future__ import annotations
from datetime import datetime
from typing import ClassVar, Self, final


@final  # marked final for singleton pattern (akin to flyweight pattern)
class TimeServer:
    """
    A singleton class, mocking a program-wide connection to a time server.

    Implements the singleton pattern.
    """

    __instance: ClassVar[TimeServer]

    __now: datetime | None

    def __new__(cls) -> Self:
        try:
            return TimeServer.__instance
        except AttributeError:
            TimeServer.__instance = self = super().__new__(cls)
            # Chained assignment:
            # - assigns to TimeServer.__instance
            # - creates a local variable self with the same value
            self.__now = None
            return self

    def now(self) -> datetime:
        """
        Returns the current date and time.

        It's a method, not a property, to communicate to the user that
        the invokation (in a real scenario would) involve(s) non-trivial
        computation and communication.

        """
        return now if (now := self.__now) else datetime.now()
        # let now := self.__now in (now if now else datetime.now())
        # if (now := self.__now) is None:
        #     now = datetime.now() # default if now not explicitly set
        # return now

    def _set_now(self, now: datetime) -> None:
        """
        Used by the mock implementation to set the now value.

        :deprecated:
        """
        self.__now = now
