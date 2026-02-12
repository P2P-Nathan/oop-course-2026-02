
from typing import TYPE_CHECKING, Self, final
if TYPE_CHECKING:
    from .user import Buyer, Seller, MarketplaceUser

@final
class Marketplace:    
    """The entry point for the marketplace library (Facade pattern)."""

    _marketplace_user_id_counter: int
    _marketplace_users: dict[str, MarketplaceUser]

    def __new__(cls) -> Self:
        self = object.__new__(cls) 
        self._marketplace_user_id_counter = 0 
        self._marketplace_users = {}
        return self

    def register_user(self, user: MarketplaceUser) -> str: 
        """Register a user in the marketplace and return their UID.""" 
        self._marketplace_user_id_counter += 1 
        uid = f"user_{self._marketplace_user_id_counter}"
        self._marketplace_users[uid] = user
        return uid