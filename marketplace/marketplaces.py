from marketplace.listings import DraftListing
from marketplace.users import Seller


class Marketplace:
    """The marketplace facade, which provides a simple interface for users to interact with the marketplace."""

    __nextListingId: int = 0

    def createListing(self, seller: Seller) -> DraftListing:
        """Create a new listing in the marketplace"""
        listingId = str(self.__nextListingId)
        self.__nextListingId += 1
        listing = DraftListing(self, seller, listingId)
        return listing
    