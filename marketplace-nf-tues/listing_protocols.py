"""Try to create some protocols / interfaces for the listing class to represent states"""

from datetime import timedelta
from decimal import Decimal
from typing import Protocol



class ListingProtocol(Protocol):
    """Protocol for all listings in any state."""
    __slots__ = ()

    title: str | None
    start_price: Decimal | None
    description: str | None
    min_bidding_time: timedelta | None

class DraftListingProtocol(ListingProtocol, Protocol):
    """Protocol for listings in the draft state."""
    __slots__ = ()

    def snapshot(self) -> dict[str, str | Decimal | timedelta | None]:
        """ Returns a snapshot of the current draft attributes. """
    def activate(self) -> None:
        """ Activate this listing, changing its state to "active". """
    def commit(self) -> None:
        """ Commits the current draft attributes as the last committed values. """
    def restore(self) -> None:
        """ Resets draft attributes to their last committed values. """