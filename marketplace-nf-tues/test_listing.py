

from .marketplace import Marketplace

myMarketplace = Marketplace()
seller = myMarketplace.createSeller("Alice")
listing = myMarketplace.createListing(seller)

print(listing)

print(listing.__dict__)