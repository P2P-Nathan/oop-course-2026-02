"""
The Bid type alias defines low-level bid data,
while the Bids class implements bid management logic.
"""

from __future__ import annotations
from collections.abc import Callable
from decimal import Decimal
from typing import Literal, Self
from .utils.stacks import WithdrawableStack

from typing import TYPE_CHECKING

#                  ^^^^^^^^^^^^^ set to true during static typechecking
#                                when circular module imports don't matter.
if TYPE_CHECKING:
    # Gate away Buyer, Username and Listing for static typechecking only,
    # you don't need to create instances, just use them as types.
    from .users import Buyer, Username
    from .listings import Listing

Bid = tuple[Buyer, Decimal]
"""
Type alias for a bid, as a (buyer, price) pair.

An example of not using a class for low-level data.
"""

BidsChange = tuple[Bid, Literal["placed", "withdrawn"]]
""" Possible bid changes. """

BidsChangedCallback = Callable[["Bids", BidsChange], None]
""" Type alias for bids change callbacks. """


class Bids:
    """
    Data structure to store bids for a listing.

    Note: Name refactored from BidStack upon suggestion from the public.
    """

    def __new__(cls, listing: Listing) -> Self:
        """Constructor for Bids, for use by Listing only."""
        # Dynamic import, to avoid circular imports.
        from .listings import Listing # Executed when constructor is called,
        #                               by that time, listings module exists.
        if not Listing._is_constructing_bids():
            raise TypeError("Bids instances cannot be constructed directly.")
        self = super().__new__(cls)
        self.__listing = listing
        self.__buyer_bids = {}
        self.__stack = WithdrawableStack()
        self.__on_bids_changed_callbacks = set()
        return self

    __listing: Listing
    __buyer_bids: dict[Username, Bid]
    __stack: WithdrawableStack[Bid]
    __on_bids_changed_callbacks: set[BidsChangedCallback]

    @property
    def listing(self) -> Listing:
        """The listing to which this Bids object belongs."""
        return self.__listing

    @property
    def top(self) -> Bid:
        """Returns the top bid, or None if there are no bids."""
        return self.__stack.peek()

    def place(self, bid: Bid) -> bool:
        """Place a new bid and returns whether placement was successful."""
        buyer, price = bid
        self._enforce_buyer_in_correct_marketplace(buyer)
        if not (stack := self.__stack):
            stack.push(bid)
            return True
        _, top_price = stack.peek()
        if price <= top_price:
            return False
        current_bid = self.__buyer_bids.get(buyer.username)
        if current_bid is not None:
            self.withdraw(buyer)
        stack.push(bid)
        self.__buyer_bids[buyer.username] = bid
        self._bids_changed((bid, "placed"))
        return True

    def withdraw(self, buyer: Buyer) -> Bid | None:
        """
        Withdraws the current bid by the buyer and returns it, if one exists.
        """
        self._enforce_buyer_in_correct_marketplace(buyer)
        username = buyer.username
        if username not in (buyer_bids := self.__buyer_bids):
            return None
        withdrawn_bid = buyer_bids[username]
        del buyer_bids[username]
        self.__stack.remove(withdrawn_bid)
        self._bids_changed((withdrawn_bid, "withdrawn"))
        return withdrawn_bid

    def _enforce_buyer_in_correct_marketplace(self, buyer: Buyer) -> None:
        """
        Method responsible for checking that the buyer is in the same
        marketplace as the listing to which this bid stack belongs.

        :raises ValueError: if the buyer is not in the correct marketplace.
        """
        if buyer.marketplace != self.listing.marketplace:
            raise ValueError(
                "Buyer and listing are not from the same marketplace."
            )

    def __bool__(self) -> bool:
        """
        Special method responsible for implicit conversion to bool,
        use when testing whether there are bids with 'if listing.bids'.

        I intentionally don't implement __len__ because the number of bids
        is not a relevant quantity, just the top one and whether there are bids.
        """
        return not self.__stack

    # == Publish-Subscribe Pattern (i.e. events) ==

    def _bids_changed(self, change: BidsChange) -> None:
        """
        Protected method responsible for triggering a bids changed event.
        """
        for callback in self.__on_bids_changed_callbacks:
            callback(self, change)

    def on_bids_changed(self, callback: BidsChangedCallback) -> None:
        """
        Registers a callback for the bids changed event.
        """
        self.__on_bids_changed_callbacks.add(callback)

    def unregister_on_bids_changed(self, callback: BidsChangedCallback) -> None:
        """
        Unregisters a callback for the bids changed event.
        """
        self.__on_bids_changed_callbacks.remove(callback)
