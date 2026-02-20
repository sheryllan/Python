from typing import List, Dict, Tuple
from collections import defaultdict

from single_order_book import SingleOrderBook
from contract_parser import parse_contract, get_expiration_date


class MultiOrderBook:
    """
    A simplified order book implementation supporting basic orders,
    matching logic, and futures contracts with expiration dates.
    """

    def __init__(self):
        """Initialize an empty order book.

        Included fields
        ----------
        contracts: Contract dictionary (contract_ticker -> single_book)
        """
        self.contracts: Dict[str, SingleOrderBook] = {}
        self.expiration_map = defaultdict(dict)

    def add_orders(self, orders: List[Dict]) -> None:
        """
        Add orders to the book and attempt to match them.

        Parameters
        ----------
        orders: List of dictionary containing order information
                   Required keys: 'type', 'price', 'quantity'
                   Optional keys: 'contract'
        """
        contract_orders = defaultdict(list)
        for order in orders:
            ticker = order.get("contract", "Unknown")
            contract_orders[ticker].append(order)

            if "contract" in order:
                product_code, expiry = parse_contract(ticker)
                self.expiration_map[product_code][expiry] = ticker

        for k, v in contract_orders.items():
            if k in self.contracts:
                self.contracts[k].add_orders(v)
            else:
                self.contracts[k] = SingleOrderBook(v, k)

    def __str__(self):
        str_list = []
        for ticker, single_book in self.contracts.items():
            str_list.append(f"\n{ticker}:" if str_list else f"{ticker}:")
            str_list.append(str(single_book))

    def view_contract_book(self, product_code: str, expiration: Tuple[int, int]) -> str:
        """
        Get a string representation for a given product and expiration.

        Parameters
        ----------
        product_code: Product code, e.g. GC for Gold
        expiration: Tuple of (year, month) of the expiration

        """
        expiry = get_expiration_date(*expiration)
        if product_code not in self.expiration_map:
            raise ValueError(f"Invalid product code: {product_code}")

        if expiry not in self.expiration_map[product_code]:
            raise ValueError(f"Expiration not found for {product_code} {expiry}")
        ticker = self.expiration_map[product_code][expiry]
        return str(self.contracts[ticker])


