"""
The Listing class implements listing logic.
"""

from __future__ import annotations
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import datetime, timedelta
from decimal import Decimal
from typing import (
    TYPE_CHECKING,
    ClassVar,
    Final,
    Literal,
    Protocol,
    Self,
    TypeGuard,
    TypedDict,
    Unpack,
)

from .bids import Bids, Bid
from .utils.time_server import TimeServer

if TYPE_CHECKING:
    from .marketplace import Marketplace
    from .users import Buyer, Seller

ListingUID = str
"""Type alias for listing UID."""

ListingState = Literal["draft", "active", "sold", "cancelled"]
"""Type alias for listing state."""

LISTING_STATES: Final[tuple[ListingState, ...]] = (
    "draft", "active", "sold", "cancelled"
)
"""
Tuple of listings states, for use at runtime.

Technically, we can get them from ListingState.__args__, but the internals of
type alias have a tendency to change once in a while, so that is only an option
if you are willing to keep up to date with breaking changes in the typing lib.
"""



class IncompleteListingData(TypedDict, total=False):
    """Data for an incomplete listing."""

    title: str
    start_price: Decimal
    description: str
    min_bid_time: timedelta


class DraftListingData(IncompleteListingData):
    """Data for a draft listing."""

    state: Literal["draft"]


class CompleteListingData(TypedDict):
    """Data for a complete listing."""

    title: str
    start_price: Decimal
    description: str
    min_bid_time: timedelta


assert (
    CompleteListingData.__annotations__ == IncompleteListingData.__annotations__
)
# A check to ensure that we don't modify one of CompleteListingData or
# IncompleteListingData without updating the other.


def is_listing_data_complete(
    data: IncompleteListingData,
) -> TypeGuard[CompleteListingData]:
    """
    A method checking that an IncompleteListingData instance has values set for
    all keys, so that it is a CompleteListingData instance.

    The return type at runtime is bool, but the TypeGuard annotation is used to
    inform static typecheckers that when this function returns True the argument
    'data'is an instance of CompleteListingData.
    """
    return all(field in data for field in CompleteListingData.__annotations__)
    #  CompleteListingData key-type pairs ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^


class ActiveListingData(CompleteListingData):
    """Data for an active listing."""
    state: Literal["active"]
    listing_time: datetime
    # bids not here because they are part of the logic, not the data.


class SoldListingData(CompleteListingData):
    """Data for a sold listing."""
    state: Literal["sold"]
    listing_time: datetime
    sell_time: datetime
    sell_price: Decimal
    buyer: Buyer


class CancelledListingData(IncompleteListingData, TypedDict):
    """Data for a cancelled listing."""
    state: Literal["cancelled"]
    cancel_time: datetime


ListingData = (
    DraftListingData
    | ActiveListingData
    | SoldListingData
    | CancelledListingData
)
"""
The ListingData type alias is what's known as a "tagged union":
a union type where individual members can be distinguished based on the value
of a "tag", in this case the "state" key.

Pylance already supports refinement of tagged union types based on tag values:

def process_data(data: ListingData) -> None:
    match data["state"]:
        case "draft":
            reveal_type(data) # Pylance: Type of "data" is "DraftListingData"
        case "active":
            reveal_type(data) # Pylance: Type of "data" is "ActiveListingData"
        case "sold":
            reveal_type(data) # Pylance: Type of "data" is "SoldListingData"
        case "cancelled":
            reveal_type(data) # Pylance: Type of "data" is "CancelledListingData"

Mypy support is still in the works.

"""


class BaseListing(Protocol):
    """Interface for properties common to all listings."""

    @property
    def marketplace(self) -> Marketplace: ...
    @property
    def seller(self) -> Seller: ...
    @property
    def uid(self) -> ListingUID: ...
    @property
    def state(self) -> ListingState: ...


class DraftListing(BaseListing, Protocol):
    """Interface exposing properties and methods of draft listings."""

    @property
    def state(self) -> Literal["draft"]: ...
    @property
    def snapshot(self) -> DraftListingData: ...
    def restore(self, snapshot: DraftListingData) -> None: ...
    def activate(self) -> ActiveListing: ...
    def cancel(self) -> CancelledListing: ...
    def set(self, **data: Unpack[DraftListingData]) -> DraftListing: ...


class CancelledListing(BaseListing, Protocol):
    """Interface exposing properties and methods of cancelled listings."""

    @property
    def state(self) -> Literal["cancelled"]: ...
    @property
    def data(self) -> CancelledListingData: ...


class ActiveListing(BaseListing, Protocol):
    """Interface exposing properties and methods of active listings."""

    @property
    def state(self) -> Literal["active"]: ...
    @property
    def data(self) -> ActiveListingData: ...
    def sell(self) -> ActiveListing: ...
    def cancel(self) -> CancelledListing: ...


class SoldListing(BaseListing, Protocol):
    """Interface exposing properties and methods of active listings."""

    @property
    def state(self) -> Literal["sold"]: ...
    @property
    def data(self) -> SoldListingData: ...
    def sell(self) -> ActiveListing: ...
    def cancel(self) -> CancelledListing: ...


ListingStateChange = (
    tuple[Literal["draft"], Literal["active"]]
    | tuple[Literal["active"], Literal["sold"]]
    | tuple[Literal["active", "draft"], Literal["cancelled"]]
)
"""Type alias for a state transition pair, as a pair of states."""

ListingStateChangedCallback = Callable[
    ["Listing", ListingStateChange],  # types of positional arguments
    None,  # return type
]
"""
Type alias for state change callbacks, which can be called by passing a
listing as their 1st arg and a :obj:`ListingStateChange` as their 2nd arg,
returning :obj:`None`.
"""
# Note: The callable type can only capture functions where all arguments can be
#       passed positionally, not ones where certain arguments must be passed
#       by name (i.e. keyword-only arguments). If you need to capture such a
#       function type, you should use Protocol to define a structural type with
#       a __call__ method, where you are free to specify positional-only,
#       positional-or-keyword, and keyword-only arguments, as usual for func's.


class StateError(Exception):
    """Custom exception class for errors relating to listing state logic."""


class Listing:
    """
    Class implementing listing logic.
    """

    # == Typeguards to narrow interface ==
    #
    # These type guards would make total sense as properties, or at the very
    # least instance methods, but unfortunately the author of PEP 647 decided
    # that this was an "unusual use case" (based on what, I don't know), so
    # this is not supported by the specs:
    #
    # - https://peps.python.org/pep-0647/#narrowing-of-implicit-self-and-cls-parameters
    # - https://github.com/python/mypy/issues/15090
    # - https://github.com/python/mypy/issues/16618
    #
    # The BasedMypy fork (which is even supported by the Mypy playground)
    # would support type guards on self for methods (but not properties), see:
    #
    # - https://kotlinisland.github.io/basedmypy/based_features.html#reinvented-type-guards
    #
    # class Listing:
    #     def is_draft(self) -> self is Self & DraftListing:
    #         return self.state == "draft"
    #

    @staticmethod
    def is_draft(listing: Listing) -> TypeGuard[DraftListing]:
        """
        Type guard to establish whether a listing is in draft state.

        .. code-block::

            if Listing.is_draft(listing):
                # IntelliSense shows DraftListing properties/methods only

        """
        return listing.state == "draft"

    @staticmethod
    def is_active(listing: Listing) -> TypeGuard[ActiveListing]:
        """
        Type guard to establish whether a listing is in draft state.

        if Listing.is_active(listing):
            # IntelliSense shows ActiveListing properties/methods only

        """
        return listing.state == "active"

    @staticmethod
    def is_sold(listing: Listing) -> TypeGuard[SoldListing]:
        """
        Type guard to establish whether a listing is in draft state.

        if Listing.is_sold(listing):
            # IntelliSense shows SoldListing properties/methods only

        """
        return listing.state == "sold"

    @staticmethod
    def is_cancelled(listing: Listing) -> TypeGuard[CancelledListing]:
        """
        Type guard to establish whether a listing is in draft state.

        if Listing.is_cancelled(listing):
            # IntelliSense shows CancelledListing properties/methods only

        """
        return listing.state == "cancelled"

    # == Bids constructor lock ==

    __is_constructing_bids: ClassVar[bool] = False

    @staticmethod
    def _is_constructing_bids() -> bool:
        """
        A flag indicating whether the Listing class logic is currently in the
        process of constructing the Bids instance for a listing which is being
        activated. Used by the Bids class constructor to disallow construction
        of Bids instances outside of Listing class logic.

        This method is protected to indicate that it is intended for developers,
        but using it does not affect the integrity of the Listing class logic,
        so it can be called by Bids without breaking encapsulation.
        """
        return Listing.__is_constructing_bids

    @staticmethod
    @contextmanager
    def __constructing_bids() -> Iterator[None]:
        """
        A context manager, used to created a context via the ``with`` statement.
        Within that context, the _is_constructing_bids class flag is
        set to True.

        See:

        - https://docs.python.org/3/library/contextlib.html#contextlib.contextmanager
        - https://docs.python.org/3/reference/compound_stmts.html#with

        """
        # 1. Ensure that we are not already constructing a Bids instance
        assert not Listing.__is_constructing_bids
        # 2. Set the class flag to True:
        Listing.__is_constructing_bids = True
        try:
            # 3. Yield control back to the calling method,
            #    which will enter the body of the 'with' context:
            yield None
        finally:
            # 4. When exiting the body of the 'with' context, restore the class
            #    flag to False, regardless of whether the context was existed
            #    normally or by raising an exception.
            Listing.__is_constructing_bids = False

    # == Constructor, attributes and state-independent properties ==

    def __new__(
        cls,
        seller: Seller,
    ) -> Self:
        """Constructor for a listing, for use by Marketplace only."""
        # Dynamic import, to avoid circular imports.
        from .marketplace import Marketplace
        if (uid := Marketplace._is_constructing_listing()) is None:
            raise TypeError("Listing instances cannot be constructed directly.")
        self = super().__new__(cls)
        self.__seller = seller
        self.__uid = uid
        self.__on_state_changed_callbacks = set()
        return self

    __marketplace: Marketplace
    __seller: Seller
    __uid: ListingUID

    __draft_data: DraftListingData
    __active_data: ActiveListingData
    __sold_data: SoldListingData
    __cancelled_data: CancelledListingData

    __state: ListingState
    __bids: Bids

    __on_state_changed_callbacks: set[ListingStateChangedCallback]

    @property
    def marketplace(self) -> Marketplace:
        """The marketplace to which this listing belongs."""
        # An example of a computed property.
        return self.seller.marketplace

    @property
    def seller(self) -> Seller:
        """The seller for this listing."""
        return self.__seller

    @property
    def uid(self) -> ListingUID:
        """The Unique ID of this listing."""
        return self.__uid

    # == Builder Pattern ==

    def set(self, **data: Unpack[DraftListingData]) -> Self:
        #                 ^^^^^^^^^^^^^^^^^^^^^^^
        # means keyword arguments are title, start_price, description,
        # and min_bid_time, with types as given in ListingSnapshot,
        # possibly not all specified (ListingSnapshot has total=False).
        """
        Method used to set/update one or more piece of data for a draft listing.

        Implements the Builder Pattern.

        Example usage:

        listing.set(title="Magic Mushrooms", description="They make you big.")
        ...
        listing.set(title="Magic Mushrooms x3", start_price=Decimal("2.5"))
        ...
        listing.set(min_bid_time=timedelta(days=14))

        Example usage with Fluent API/Interface Pattern:

        listing.set(title="Magic Mushrooms")
               .set(description="They make you big.")
               .set(start_price=Decimal("2.5"))
               .set(min_bid_time=timedelta(days=14))

        In another branch of the multiverse, I would have implemented a more
        literate, but less scalable version:

        listing.titled("Magic Mushrooms")
               .described_as("They make you big.")
               .with_start_price(Decimal("2.5"))
               .with_min_bid_time(timedelta(days=14))

        This is an example of what embedded domain specific languages
        for promises/queries typically look like.

        """
        self.restore(data)
        return self  # Fluent API/Interface Pattern, allows method chaining

    # == Memento Pattern ==

    @property
    def snapshot(self) -> DraftListingData:
        """
        Returns a listing snapshot, a possibly partial view of the listing data.

        Part of the Memento Pattern implementation.
        """
        return {**self.__draft_data}  # same as self._data.copy()

    def restore(self, snapshot: DraftListingData) -> None:
        """
        The method responsible for setting draft listing data,
        including its validation.

        Part of the Memento Pattern implementation.

        :raises StateError: if the listing is not in draft state.
        """
        if self.state != "draft":
            raise StateError("Only draft listings can be restored.")
        if (title := snapshot.get("title")) is not None:
            if not title:
                raise ValueError("Title cannot be empty.")
            if len(title) > 50:
                raise ValueError("Title length must be at most 50.")
        if (description := snapshot.get("title")) is not None:
            if not description:
                raise ValueError("Description cannot be empty.")
            if len(description) > 500:
                raise ValueError("Description length must be at most 500.")
        if (start_price := snapshot.get("start_price")) is not None:
            if start_price < 0:
                raise ValueError("Start price cannot be negative.")
        if (min_bid_time := snapshot.get("min_bid_time")) is not None:
            if min_bid_time < timedelta(days=0):
                raise ValueError("Min bidding time cannot be negative.")
        self.__draft_data.update(snapshot)

    # == Prototype Pattern ==

    def clone(self, seller: Seller) -> Listing:
        """
        Creates a draft listing for a new seller,
        using the data for this listing as a blueprint.

        Implements the Prototype Pattern.
        """
        # 1. Create a draft listing for the given seller in their marketplace
        listing = seller.marketplace.draft_listing(seller)
        # 2. Fill the draft listing with the current listing data
        listing.restore(self.snapshot)
        # 3. Return the draft listing
        return listing

    # == State Pattern ==

    @property
    def state(self) -> ListingState:
        """The state of a listing."""
        return self.__state

    @property
    def data(self) -> ListingData:
        """The data of a listing, as a union type tagged by listing state."""
        match self.state:
            case "draft":
                return self.__draft_data
            case "active":
                return self.active_data
            case "sold":
                return self.sold_data
            case "cancelled":
                return self.cancelled_data

    @property
    def bids(self) -> Bids:
        """
        Object/sub-component responsible for bidding logic on an active listing.
        """
        if self.state != "active":
            raise StateError("Only active listings have bids.")
        return self.__bids

    @property
    def draft_data(self) -> DraftListingData:
        """Exposes the data of a draf listing."""
        if self.state != "draft":
            raise StateError("Listing is not draft.")
        return {**self.__draft_data}

    @property
    def active_data(self) -> ActiveListingData:
        """Exposes the data of a active listing."""
        if self.state != "active":
            raise StateError("Listing is not active.")
        return {**self.__active_data}

    @property
    def sold_data(self) -> SoldListingData:
        """Exposes the data of a sold listing."""
        if self.state != "sold":
            raise StateError("Listing is not sold.")
        return {**self.__sold_data}

    @property
    def cancelled_data(self) -> CancelledListingData:
        """Exposes the data of a cancelled listing."""
        if self.state != "cancelled":
            raise StateError("Listing is not cancelled.")
        return {**self.__cancelled_data}

    def activate(self) -> None:
        """Performs a listing state transition from draft to active."""
        if (state := self.state) != "draft":
            raise StateError("Only draft listings can be activated.")
        draft_data = self.__draft_data
        if not is_listing_data_complete(draft_data):
            raise StateError("Cannot activate incomplete listings.")
        # Here, static type checkers know that draft_data: CompleteListingData,
        # thanks to the TypeGuard return type hint in is_listing_data_complete.
        self.__active_data = {
            **draft_data,
            "state": "active",
            # To my surprise, Mypy recognises that "state" from _draft data
            # is overwritten to "sold", so that this is valid _active_data.
            "listing_time": TimeServer().now(),
        }
        self.__state = "active"
        with Listing.__constructing_bids():
            self.__bids = Bids(self)
        self._state_changed((state, "active"))

    def sell(self) -> None:
        """Performs a listing state transition from active to sold."""
        if (state := self.state) != "active":
            raise StateError("Only active listings can be sold.")
        if not self.bids:
            raise StateError("Cannot sell a listing without bids.")
        active_data = self.active_data
        sell_time = TimeServer().now()
        if (
            sell_time - active_data["listing_time"]
            < active_data["min_bid_time"]
        ):
            raise StateError("Cannot sell listing, not enough time elapsed.")
        buyer, price = self.bids.top
        self.__sold_data = {
            **active_data,
            "state": "sold",
            "sell_time": sell_time,
            "sell_price": price,
            "buyer": buyer,
        }
        self.__state = "sold"
        # Clear data no longer accessible from memory:
        del self.__active_data
        del self.__bids
        # Because the bids are not part of the ActiveListingData and the
        # bids property only exposes them in the active state,
        # I can unlink the bids from this object and let the garbage colllector
        # do its job (unless someone kept a reference to Bids somewhere else,
        # but it doesn't matter anymore).
        self._state_changed((state, "sold"))

    def cancel(self) -> None:
        """
        Performs a listing state transition from draft or active to cancelled.
        """
        cancel_time = TimeServer().now()
        if (state := self.state) == "active":
            if self.bids:
                raise StateError("Cannot cancel an active listing with bids.")
            # Clear data no longer accessible from memory:
            del self.__bids
            del self.__active_data
        elif state != "draft":
            raise StateError("Only draft or active listings can be cancelled.")
        self.__cancelled_data = {
            **self.__draft_data,
            "state": "cancelled",
            "cancel_time": cancel_time,
        }
        self.__state = "cancelled"
        self._state_changed((state, "cancelled"))

    # == Publish-Subscribe Pattern (i.e. events) ==

    def _state_changed(self, change: ListingStateChange) -> None:
        """
        Protected method responsible for triggering a state changed event.
        """
        for callback in self.__on_state_changed_callbacks:
            callback(self, change)

    def on_state_changed(self, callback: ListingStateChangedCallback) -> None:
        """
        Registers a callback for the state changed event.
        """
        self.__on_state_changed_callbacks.add(callback)

    def unregister_on_state_changed(
        self, callback: ListingStateChangedCallback
    ) -> None:
        """
        Unregisters a callback for the state changed event.
        """
        self.__on_state_changed_callbacks.remove(callback)
