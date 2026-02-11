from datetime import timedelta
from decimal import Decimal
from typing import TYPE_CHECKING, Literal, Self, TypedDict



if TYPE_CHECKING:
    from .user import Seller
    from .marketplace import Marketplace
    from .listing_protocols import DraftListingProtocol

type ListingState = Literal["draft", "active", "sold", "cancelled"]
"""Possible states for a listing."""

class ListingData(TypedDict, total=False):
    """A data container for listing attributes."""
    title: str 
    start_price: Decimal 
    description: str
    min_bidding_time: timedelta 


class Listing:
    """A listing in a marketplace."""

    # Immutable attributes:
    _marketplace: Marketplace
    _seller: Seller
    _uid: str

    # Internally mutable attributes:
    _state: ListingState

    # Externally mutable attributes:
    # TODO: I will refactor these into a separate container (typed dictionary),
    #       when implementing the memento pattern tomorrow.
    _title: str | None # Optional[T] is implemented as T | None
    _start_price: Decimal | None
    _description: str | None
    _min_bidding_time: timedelta | None

    _data : ListingData | None

    __draft_title: str | None
    __draft_start_price: Decimal | None
    __draft_description: str | None
    __draft_min_bidding_time: timedelta | None

    def __new__(cls, marketplace: Marketplace, seller: Seller, uid: str) -> Self:
        # TODO: ensure that the listing is being constructed legally.
        #       Possible options:
        #       - Notify the marketplace via some callback method.
        #       - Guard this with a lock managed by the marketplace.
        #       - Ask the marketplace for a new UID (I like this the best)
        self = object.__new__(cls)
        self._state = "draft"
        self._marketplace = marketplace
        self._seller = seller
        self._uid = uid
        self.__draft_title = None
        self.__draft_start_price = None
        self.__draft_description = None
        self.__draft_min_bidding_time = None
        return self
    
    # Read-only properties:

    @property
    def marketplace(self) -> Marketplace:
        """The marketplace this listing belongs to."""
        return self._marketplace
    
    @property
    def seller(self) -> Seller:
        """The seller who created this listing."""
        return self._seller
    
    @property
    def uid(self) -> str:
        """The unique identifier for this listing."""
        return self._uid
    
    @property
    def state(self) -> ListingState:
        """The current state of this listing."""
        return self._state
    
    # Read-write properties:
    
    @property
    def title(self) -> str | None:
        """The title of this listing."""
        if self._state == "draft":
            return self.__draft_title
        else:
            return self._title
    
    @title.setter
    def title(self, title: str) -> None:
        # TODO: Validate that listing is in draft.
        # Validate title length:
        if len(title) > 50:
            raise ValueError("Title must be at most 50 characters long.")
        if self._state == "draft":
            self.__draft_title = title
        else:
            raise ValueError("Cannot set title of a listing that is not in the draft state.")

    @property
    def start_price(self) -> Decimal | None:
        """The starting price of this listing."""
        if self._state == "draft":
            return self.__draft_start_price
        else:
            return self._start_price
    
    @start_price.setter
    def start_price(self, price: Decimal) -> None:
        # TODO: Validate that listing is in draft.
        # Validate that price is non-negative:
        if price < 0:
            raise ValueError("Starting price must be non-negative.")
        if self._state == "draft":
            self.__draft_start_price = price
        else:
            raise ValueError("Cannot set start price of a listing that is not in the draft state.")

    @property
    def description(self) -> str | None:
        """The description of this listing."""
        if self._state == "draft":
            return self.__draft_description
        else:
            return self._description
    
    @description.setter
    def description(self, description: str) -> None:
        # TODO: Validate that listing is in draft.
        # Validate description length:
        if len(description) > 500:
            raise ValueError("Description must be at most 500 characters long.")
        if self._state == "draft":
            self.__draft_description = description
        else:
            raise ValueError("Cannot set description of a listing that is not in the draft state.")
    
    @property
    def min_bidding_time(self) -> timedelta | None:
        """The minimum bidding time for this listing."""
        if self._state == "draft":
            return self.__draft_min_bidding_time
        else:            
            return self._min_bidding_time
    
    @min_bidding_time.setter
    def min_bidding_time(self, time: timedelta) -> None:
        # TODO: Validate that listing is in draft.
        # Validate that minimum bidding time is at least 1 minute:
        if time < timedelta(minutes=1):
            raise ValueError("Minimum bidding time must be at least 1 minute.")
        if self._state == "draft":
            self.__draft_min_bidding_time = time
        else:
            raise ValueError("Cannot set minimum bidding time of a listing that is not in the draft state.")

    # Prototype pattern implementation:

    def clone(self, seller: Seller, uid: str) -> DraftListingProtocol:
        # Responsibility for handling the validity of the listing construction
        # is delegated to the constructor Listing.__new__:
        clone = Listing(self.marketplace, seller, uid)
        # Note: the listing clone is created in the "draft" state.
        # TODO: set additional listing attributes.
        clone.__draft_title = self._title if self._title is not None else self.__draft_title
        clone.__draft_start_price = self._start_price if self._start_price is not None else self.__draft_start_price
        clone.__draft_description = self._description if self._description is not None else self.__draft_description
        clone.__draft_min_bidding_time = self._min_bidding_time if self._min_bidding_time is not None else self.__draft_min_bidding_time
        return clone
    
    # State transition methods:
    def activate(self) -> None:
        """ Activate this listing, making it visible to buyers. """
        if self._state != "draft":
            raise ValueError("Can only activate a listing in the draft state.")
        if self.__draft_title is None or self.__draft_start_price is None or self.__draft_description is None or self.__draft_min_bidding_time is None:
            raise ValueError("Cannot activate a listing with unset attributes.")
        self.commit()
        self._state = "active"

    def cancel(self) -> None:
        """ Cancel this listing, making it unavailable for bidding. """
        if self._state != "active":
            raise ValueError("Can only cancel a listing in the active state.")
        self._state = "cancelled"

    def sell(self) -> None:
        """ Mark this listing as sold. """
        # TODO: check bids and buyer information before selling the listing.
        if self._state != "active":
            raise ValueError("Can only sell a listing in the active state.")
        self._state = "sold"

    # Memento pattern implementation:
    def restore(self) -> None:
        """ Resets draft attributes to their last committed values. """
        if(self._state != "draft"):
            raise ValueError("Can only restore a listing in the draft state.")
        self.__draft_title = self._title
        self.__draft_start_price = self._start_price
        self.__draft_description = self._description
        self.__draft_min_bidding_time = self._min_bidding_time

    def commit(self) -> None:
        """ Commits the current draft attributes as the last committed values. """
        if(self._state != "draft"):
            raise ValueError("Can only commit a listing in the draft state.")
        self._title = self.__draft_title
        self._start_price = self.__draft_start_price
        self._description = self.__draft_description
        self._min_bidding_time = self.__draft_min_bidding_time

    def snapshot(self) -> dict[str, str | Decimal | timedelta | None]:
        """ Returns a snapshot of the current live attributes. """
        if(self._state != "draft"):
            raise ValueError("Can only take a snapshot of a listing in the draft state.")
        return {
            "title": self._title,
            "start_price": self._start_price,
            "description": self._description,
            "min_bidding_time": self._min_bidding_time
        }