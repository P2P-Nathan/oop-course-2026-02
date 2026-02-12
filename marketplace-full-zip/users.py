"""
The Buyer and Seller classes, respectively, implement functionality
for buyers and sellers in the marketplace.
"""

from __future__ import annotations
from abc import ABCMeta
from collections.abc import Mapping
from contextlib import contextmanager
from decimal import Decimal
import re
from types import MappingProxyType
from typing import TYPE_CHECKING, ClassVar, Iterator, Literal, Self, overload

from .bids import Bid, Bids, BidsChange
from .listings import LISTING_STATES, ActiveListing, CancelledListing, DraftListing, Listing, ListingState, ListingUID, ListingStateChange, SoldListing
if TYPE_CHECKING:
    from .marketplace import Marketplace

Username = str
"""Type alias for a username (for documentation purposes)."""


class BaseUser(metaclass=ABCMeta):
    """
    Abstract base class for marketplace users.
    Responsible for instance construction and managing user data common to
    different user roles.
    """

    # == Constructor, attributes and properties ==

    def __new__(
        cls,
        marketplace: Marketplace,
        username: Username,
    ) -> Self:
        """Constructor for a base user, for use by Marketplace only."""
        # Dynamic import, to avoid circular imports.
        from .marketplace import Marketplace
        if not Marketplace._is_constructing_user():
            raise TypeError(
                "BaseUser instances cannot be constructed directly."
            )
        # TODO: raise error if cls is BaseUser
        self = super().__new__(cls)
        self.__marketplace = marketplace
        self.__username = username
        return self

    __marketplace: Marketplace
    __username: Username

    @property
    def marketplace(self) -> Marketplace:
        """The marketplace to which the user belongs."""
        return self.__marketplace

    @property
    def username(self) -> Username:
        """The username uniquely identifying the user in the marketplace."""
        return self.__username


class Buyer(BaseUser):
    """Class for a marketplace buyer."""

    # == Constructor, attributes and properties ==

    def __new__(
        cls,
        marketplace: Marketplace,
        username: Username,
    ) -> Self:
        """Constructor for a buyer, for use by Marketplace only."""
        self = super().__new__(cls, marketplace, username)
        self.__bids_on_active_listings = {}
        self.__listings_bought = {}
        self.__amount_on_highest_bids = Decimal(0)
        self.__amount_spent = Decimal(0)
        return self

    __bids_on_active_listings: dict[ListingUID, Bid]
    __listings_bought: dict[ListingUID, Listing]
    __amount_on_highest_bids: Decimal
    __amount_spent: Decimal

    @property
    def bids_on_active_listings(self) -> Mapping[ListingUID, Bid]:
        """Bids by this buyer on active listings, indexed by listing UID."""
        return MappingProxyType(self.__bids_on_active_listings)
        #      ^^^^^^^^^^^^^^^^ creates a read-only view on a dictionary

    @property
    def listings_bought(self) -> Mapping[ListingUID, Listing]:
        """Listings bought by this buyer, indexedby listing UID."""
        return MappingProxyType(self.__listings_bought)

    @property
    def amount_on_highest_bids(self) -> Decimal:
        """
        Total amount currently on highest bids by this buyer on active listings.
        """
        return self.__amount_on_highest_bids

    @property
    def amount_spent(self) -> Decimal:
        """Total amount spent by this buyer on sold listings."""
        return self.__amount_spent

    # == Buyer functionality ==

    def place_bid(self, listing: Listing, amount: Decimal) -> bool:
        """Places a bid on a listing, returning whether this was successful."""
        return listing.bids.place((self, amount))

    def withdraw_bid(self, listing: Listing) -> Decimal | None:
        """
        Withdraws the current bid by this buyer and returns the amoutn,
        or None if the bid didn't exist.
        """
        bid = listing.bids.withdraw(self)
        return None if bid is None else bid[1]

    # == Handlers for Publish-Subscribe pattern ==

    def _handle_listing_state_changed(
        self,
        listing: Listing,
        _: ListingStateChange
    ) -> None:
        """
        Callback handling state changes on listings where the buyer has a bid.
        """
        data = listing.sold_data
        if data["buyer"] == self:
            # The listing was bought by this buyer
            self.__amount_spent += (sell_price := data["sell_price"])
            self.__amount_on_highest_bids -= sell_price
            self.__listings_bought[listing.uid] = listing
        # Regardless, the listing has sold, remove the bid
        del self.__bids_on_active_listings[listing.uid]

    def _handle_bids_changed(
        self,
        bids: Bids,
        change: BidsChange
    ) -> None:
        """
        Callback handling bids changes on listings where the buyer has a bid.
        """
        (user, amount), event = change
        if event == "withdrawn":
            (top_user, top_amount) = bids.top
            if user == self:
                if amount > top_amount:
                    # This buyer's withdrawn bid was the highest bid
                    self.__amount_on_highest_bids -= amount
                # Regardless, remove the bid
                del self.__bids_on_active_listings[bids.listing.uid]
            elif  top_user == self:
                # This buyer's bid is now the highest bid
                self.__amount_on_highest_bids += amount
        else: # event == "placed"
            # This user's bid is necessarily the highest bid
            self.__amount_on_highest_bids += amount
            self.__bids_on_active_listings[bids.listing.uid] = (user, amount)

class Seller(BaseUser):
    """Class for a marketplace seller."""

    # == Constructor, attributes and properties ==

    def __new__(
        cls,
        marketplace: Marketplace,
        username: Username,
    ) -> Self:
        """Constructor for a base user, for use by Marketplace only."""
        self = super().__new__(cls, marketplace, username)
        self.__listings = {state: {} for state in LISTING_STATES}
        self.__amount_earned = Decimal(0)
        return self

    __listings: dict[ListingState, dict[ListingUID, Listing]]
    __amount_earned: Decimal

    def listings(self, state: ListingState) -> Mapping[ListingUID, Listing]:
        """Method to access seller's listings by listing state."""
        return MappingProxyType(self.__listings[state])

    @property
    def amount_earned(self) -> Decimal:
        """Total amount earned by the seller on sold listings."""
        return self.__amount_earned

    # == Seller functionality ==

    def draft_listing(self) -> Listing:
        """Creates a draft listing for this seller."""
        return self.marketplace.draft_listing(self)

    def clone_listing(self, listing: Listing) -> Listing:
        """
        Creates a new listing for this seller,
        using a given listings as a blueprint.
        """
        return listing.clone(self)

    # == Handlers for Publish-Subscribe pattern ==

    def _handle_listing_state_changed(
        self,
        listing: Listing,
        change: ListingStateChange
    ) -> None:
        """
        Callback handling state changes on listings by the seller.
        """
        assert listing.seller == self
        previous_state, current_state = change
        # 1. Migrate listing within internal storage:
        del self.__listings[previous_state][listing.uid]
        self.__listings[current_state][listing.uid] = listing
        if current_state == "sold":
            # 2. If listing was sold, update amount earned
            self.__amount_earned += listing.sold_data["sell_price"]

