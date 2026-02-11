"""Bid type alias and the BidStack implementation of WithdrawableStack."""

from decimal import Decimal
from typing import Self

from .user import Seller
from .utils.withdrawableStack import WithdrawableStack


type Bid = tuple[Seller, Decimal]

class BidStack():
    """A stack of bids, where each bid is a tuple of (Seller, Decimal)."""

    __bids: WithdrawableStack[Bid] = None

    def __new__(cls) -> Self:
        self = object.__new__(cls)
        self.__bids = WithdrawableStack[Bid]()
        return self
    
    def place(self, bid: Bid) -> None:
        """Place a bid on the stack."""

        if(self.__bids and bid[1] <= self.__bids.peek()[1]):
            raise ValueError(f"Bid {bid} is not higher than the current top bid {self.__bids.peek()}")

        self.__bids.push(bid)

    def withdraw(self, bid: Bid) -> None:
        """Withdraw a bid from the stack."""
        self.__bids.remove(bid)

    def top(self) -> Bid:
        """Return the top bid on the stack."""
        return self.__bids.peek()
    
    def has_bids(self) -> bool:
        """Return True if the stack has any bids, False otherwise."""
        return len(self.__bids) > 0