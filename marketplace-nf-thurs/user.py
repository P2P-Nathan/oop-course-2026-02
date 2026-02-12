
from typing import TYPE_CHECKING, Literal, Protocol, Self, runtime_checkable
if TYPE_CHECKING:
    from .marketplace import Marketplace
    from .listing import DraftListing, ConcreteListing

@runtime_checkable
class MarketplaceUser(Protocol):
    """A user in a marketplace."""
    __slots__ = ()

    @property
    def marketplace(self) -> Marketplace: ...

    @property
    def UID(self) -> str: ...
    
    @property
    def user_type(self) -> Literal["seller", "buyer"]: ...


class Seller(MarketplaceUser):
    """A seller in a marketplace."""
    _marketplace: Marketplace
    _UID: str

    def __new__(cls, marketplace: Marketplace) -> Self:
        self = object.__new__(cls)
        self._marketplace = marketplace
        self._UID = marketplace.register_user(self)
        return self

    @property
    def marketplace(self) -> Marketplace:
        return self._marketplace
    
    @property
    def UID(self) -> str: 
        return self._UID

    def draft_listing(self) -> DraftListing:
        """Create a new listing in the "draft" state."""
        uid = "dummy" # FIXME: this is just a dummy value
        return ConcreteListing.draft(self._marketplace, self, uid)

class Buyer(MarketplaceUser):
    """A buyer in a marketplace."""