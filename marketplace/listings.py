from datetime import timedelta
from decimal import Decimal
from typing import Literal, Self

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .users import Buyer, Seller
    from .marketplaces import Marketplace

type ListingState = Literal["Draft", "Active", "Sold", "Cancelled"]

class Listing:
    """A listing within the marketplace"""
    # Fixed / immutable properties:

    
    _marketplace: Marketplace
    _seller: Seller

    # Internal mutable properties:
    _listingId: str
    _state: ListingState

    # Externally mutable properties:
    _price: Decimal | None
    _title: str | None
    _description: str | None
    _min_bidding_time: timedelta | None

    def __new__(cls, marketplace: Marketplace, seller: Seller, listingId: str) -> Self:

        self = object.__new__(cls)
        self._marketplace = marketplace
        self._seller = seller
        self._listingId = listingId
        self._state = "Draft"
        self._price = None
        self._title = None
        self._description = None
        self._min_bidding_time = None
        return self
    
    # Properties for safe read-only

    @property
    def marketplace(self) -> Marketplace:
        """The marketplace this listing belongs to."""
        return self._marketplace
    
    @property
    def seller(self) -> Seller:
        """The seller who created this listing."""
        return self._seller
    
    @property
    def listingId(self) -> str:
        """The unique identifier for this listing."""
        return self._listingId
    
    # Read-write properties for externally mutable data:
    @property
    def title(self) -> str | None:
        """The title of the listing."""
        return self._title
    
    @title.setter
    def title(self, newTitle: str) -> None:
        """Set a new title for the listing."""
        if len(newTitle) == 0:
            raise ValueError("Title cannot be empty")
        if len(newTitle) > 50:
            raise ValueError("Title cannot be longer than 50 characters")
        self._title = newTitle
    
    @property
    def price(self) -> Decimal | None:
        """The price of the listing."""
        return self._price

    # Instance methods

    # Prototype for a method to clone a listing into a new draft variant, which can be used to create a new listing based on an existing one.

    def clone(self, newSeller: Seller, newListing: str) -> DraftListing:
        """Clone this listing into a new draft variant"""
        clone = DraftListing(self._marketplace, newSeller, newListing)
        return clone


class DraftListing(Listing):
    """This represnets a listing which is in the Draft state and can be modified"""
    def __new__(cls, marketplace: Marketplace, seller: Seller, listingId: str) -> Self:
        self = object.__new__(cls)
        self._marketplace = marketplace
        self._seller = seller
        self._listingId = listingId
        return self
    
    # Instance methods

