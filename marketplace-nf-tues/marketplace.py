
from typing import TYPE_CHECKING, Self

from .listing import Listing
from .listing_protocols import DraftListingProtocol
from .user import Seller


class Marketplace:    
    """The entry point for the marketplace library (Facade pattern)."""

    __currentListingId: int

    def __new__(cls) -> Self:
        self = object.__new__(cls)
        self.__currentListingId = 0
        return self
        
    def createListing(self, seller: Seller) -> DraftListingProtocol:
        """Create a new listing in the marketplace."""
        listingId = str(self.__currentListingId)
        self.__currentListingId += 1
        listing = Listing(self, seller, listingId)
        return listing
    
    def createSeller(self, name: str) -> Seller:
        """Create a new seller in the marketplace."""
        return Seller(name)
