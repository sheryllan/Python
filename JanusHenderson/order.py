from typing import Optional
from enum import Enum
from dataclasses import dataclass


class OrderType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


@dataclass
class Order:
    """Represents a single order in the order book."""

    type: str
    price: float
    quantity: int
    contract: Optional[str] = None

    def __post_init__(self):
        """Validate the order fields after initialization."""

        # OrderType will throw a ValueError if invalid type string is entered
        self.type = OrderType(self.type.upper()).value
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.price <= 0:
            raise ValueError("Price must be positive")

    def __str__(self):
        """
        The string representation of the order.

        Examples
        ----------
        contract is not set: BUY 5@102
        contract is set: 2@1500 on GCQ4 Comdty
        """
        s = f"{self.type} {self.quantity}@{self.price}"
        if self.contract:
            s = f"{s} on {self.contract}"
        return s
