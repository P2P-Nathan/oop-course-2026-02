"""
The Marketplace class provides the façade for all marketplace functionality
in the library.
"""

from __future__ import annotations
from collections.abc import Iterator
from contextlib import contextmanager
from types import MappingProxyType
from typing import ClassVar, Mapping, Protocol, Self, Type, TypeVar, cast, final
from uuid import uuid4
from weakref import WeakValueDictionary

from .listings import Listing, ListingUID
from .users import BaseUser, Buyer, Seller, Username

UserT = TypeVar("UserT", bound=BaseUser)
"""
A type variable for a user class, as a subclass of BaseUser.
"""

class _MarketplaceUsers(Protocol):
    """
    Interface for the data structure used to store users within Marketplace.
    """

    def __getitem__(self, user_cls: Type[UserT], /) -> dict[Username, UserT]:
        """
        Given a subclass of BaseUser, it returns a dictionary mapping usernames
        to instances of that subclass.
        """

    def setdefault(
        self,
        user_cls: Type[UserT],
        default: dict[Username, UserT], /
    ) -> dict[Username, UserT]:
        """
        Given a subclass of BaseUser and a default dictionary mapping usernames
        to instances of that subclass, returns a dictionary mapping usernames
        to instances of that subclass (either the one previously stored, or the
        given default value if none was previously stored).
        """

@final # marked final because of the Flyweight pattern.
class Marketplace:

    # == Listing/BaseUser constructor locks ==

    __is_constructing_listing: ClassVar[ListingUID | None] = None

    @staticmethod
    def _is_constructing_listing() -> ListingUID | None:
        """
        A variable indicating whether the Marketplace logic is constructing a
        Listing instance, and if so what the listing UID is.
        Used by the Listing class constructor to disallow construction of
        Listing instances outside of Marketplace class logic, and to internally
        obtain the UID from the marketplace.
        """
        return Marketplace.__is_constructing_listing

    @staticmethod
    @contextmanager
    def __constructing_listing() -> Iterator[None]:
        """
        A context manager, used to created a context via the ``with`` statement.
        Within that context, the `_is_constructing_listing` class flag is
        set to a fresh listing UID value.
        """
        # 1. Ensure that we are not already constructing a Listing instance
        assert Marketplace.__is_constructing_listing is None
        # 2. Set the class var to a fresh listing UID:
        Marketplace.__is_constructing_listing = str(uuid4())
        try:
            # 3. Yield control back to the calling method,
            #    which will enter the body of the 'with' context:
            yield None
        finally:
            # 4. When exiting the body of the 'with' context, restore the class
            #    var to None, regardless of whether the context was existed
            #    normally or by raising an exception.
            Marketplace.__is_constructing_listing = None

    __is_constructing_user: ClassVar[bool] = False

    @staticmethod
    def _is_constructing_user() -> bool:
        """
        A flag indicating whether the Marketplace logic is constructing a
        BaseUser instance. Used by the Listing class constructor to disallow
        construction of BaseUser instances outside of Marketplace class logic.
        """
        return Marketplace.__is_constructing_user

    @staticmethod
    @contextmanager
    def __constructing_user() -> Iterator[None]:
        """
        A context manager, used to created a context via the ``with`` statement.
        Within that context, the `_is_constructing_user` class flag is
        set to True.
        """
        # 1. Ensure that we are not already constructing a Bids instance
        assert not Marketplace.__is_constructing_user
        # 2. Set the class flag to True:
        Marketplace.__is_constructing_user = True
        try:
            # 3. Yield control back to the calling method,
            #    which will enter the body of the 'with' context:
            yield None
        finally:
            # 4. When exiting the body of the 'with' context, restore the class
            #    flag to False, regardless of whether the context was existed
            #    normally or by raising an exception.
            Marketplace.__is_constructing_user = False

    # == Constructor, attributes and properties ==

    __instances: ClassVar[
        WeakValueDictionary[str, Marketplace]
    ] = WeakValueDictionary()

    def __new__(cls, uid: str) -> Self:
        """
        Constructs a new marketplace given a unique ID.

        Implements the Flyweight Pattern, so that a single live intance is
        responsible for each marketplace's data (uniquely identified by UID).

        """
        self = Marketplace.__instances.get(uid)
        if self is None:
            self = super().__new__(cls)
            self.__uid = uid
            self.__users = cast(_MarketplaceUsers, {})
            self.__listings = {}
            Marketplace.__instances[uid] = self
        return self

    __uid: str
    __users: _MarketplaceUsers
    __listings: dict[ListingUID, Listing]

    @property
    def uid(self) -> str:
        """The unique identifier for the marketplace."""
        return self.__uid

    @property
    def listings(self) -> Mapping[ListingUID, Listing]:
        """The listings of this marketplace, indexed by UID."""
        return MappingProxyType(self.__listings)

    # == Marketplace functionality ==

    def buyer(self, username: Username) -> Buyer:
        """
        Factory method responsible for the creation/retrieval of a buyer.
        """
        return self.__user(Buyer, username)

    def seller(self, username: Username) -> Seller:
        """
        Factory method responsible for the creation/retrieval of a seller.
        """
        return self.__user(Seller, username)

    def draft_listing(self, seller: Seller) -> Listing:
        """
        Factory method responsible for the creation of a draft listing for a
        given seller in this marketplace.
        """
        if seller.marketplace != self:
            raise ValueError("Seller is not from this marketplace.")
        with self.__constructing_listing():
            listing = Listing(seller)
            self.__listings[listing.uid] = listing
            return listing

    def __user(self, user_cls: Type[UserT], username: Username) -> UserT:
        """
        Private method responsible for storing and retrieving users,
        indexed by user class (currently, Buyer or Seller) and username.

        A pretty typical implementation of the factory pattern, including
        assumptions about the behaviour of specific subclass constructors
        for the BaseUser class (specifically, that they construct an instance
        by taking the username as their only argument).
        """
        users = self.__users.setdefault(user_cls, {})
        user = users.get(username)
        if user is None:
            with Marketplace.__constructing_user():
                user = user_cls(self, username)
                # Presumes that constructors for relevant BaseUser subclasses
                # take the username as their unique (positional) argument
            users[username] = user
        return user
