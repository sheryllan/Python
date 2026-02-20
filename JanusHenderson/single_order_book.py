from typing import List, Dict
from collections import OrderedDict

from order import Order, OrderType


class SingleOrderBook:
    """
    The order book for a single instrument.
    """
    PRINT_ORDER_FORMAT = r"Price: {}, Quantity: {}"

    def __init__(self, orders: List[Dict] = None, ticker: str = None):
        """
        Add initial orders to the book, separating them into buy_orders and sell_orders and grouping them by price.

        Orders are stored in OrderedDict objects (price -> orders) in order to preserve the intended ordering of the keys.
        Use price as str for the dictionary key to avoid inaccurate float comparison.
        buy_orders keys are preserved in descending order and sell_orders key in ascending order.
        """
        self.buy_orders: OrderedDict = {}
        self.sell_orders: OrderedDict = {}
        self.ticker = ticker
        if orders:
            self.add_orders(orders)

    def add_orders(self, orders: List[Dict]) -> None:
        """
        Add orders to the book and attempt to match them.

        Parameters
        ----------
        orders: List of dictionary containing order information
                   Required keys: 'type', 'price', 'quantity'
                   Optional keys: 'contract'
        """
        for order_dict in orders:
            order = Order(**order_dict)
            price = order.price
            if order.type == OrderType.BUY:
                if price in self.buy_orders:
                    self.buy_orders[price].append(order)
                else:
                    self.buy_orders[price] = [order]
            else:
                if price in self.sell_orders:
                    self.sell_orders[price].append(order)
                else:
                    self.sell_orders[price] = [order]

        self.match_orders()

    def match_orders(self) -> None:
        """
        Try to match the buy_orders and sell_orders in the book by matching their keys in order,
        crossing off the matched orders.
        """
        if not (self.buy_orders and self.sell_orders):
            print(self)
            return

        # Sorted price levels for order matching
        buy_prices = sorted(self.buy_orders, reverse=True)
        sell_prices = sorted(self.sell_orders)

        # Update the buy_orders and sell_orders with the desired key ordering
        self.buy_orders = OrderedDict((x, self.buy_orders[x]) for x in buy_prices)
        self.sell_orders = OrderedDict((x, self.sell_orders[x]) for x in sell_prices)

        i, j = 0, 0  # the index of a buy/sell price level
        while i < len(buy_prices) and j < len(sell_prices) and buy_prices[i] >= sell_prices[j]:
            buy_price = buy_prices[i]
            sell_price = sell_prices[j]
            buy_orders_at_price = self.buy_orders[buy_price]
            sell_orders_at_price = self.sell_orders[sell_price]

            p, q = 0, 0  # the index of an order at the given price level
            while p < len(buy_orders_at_price) and q < len(sell_orders_at_price):
                buy_order = buy_orders_at_price[p]
                sell_order = sell_orders_at_price[q]
                self.print_match(buy_order, sell_order)
                if buy_order.quantity > sell_order.quantity:
                    buy_order.quantity -= sell_order.quantity
                    q += 1
                elif sell_order.quantity > buy_order.quantity:
                    sell_order.quantity -= buy_order.quantity
                    p += 1
                else:
                    p += 1
                    q += 1

                # Update the order book removing the fully matched orders
                if buy_orders_at_price[p:]:
                    self.buy_orders[buy_price] = buy_orders_at_price[p:]
                else:
                    self.buy_orders.pop(buy_price)
                    i += 1

                if sell_orders_at_price[q:]:
                    self.sell_orders[sell_price] = sell_orders_at_price[q:]
                else:
                    self.sell_orders.pop(sell_price)
                    j += 1

                # Print current orders in the book after matching
                print(str(self) + "\n")

    def print_match(self, buy_order: Order, sell_order: Order):
        """Print the match information"""

        buy_order_str = str(buy_order).split(" on")[0]
        print(f"Match: {buy_order_str} with {sell_order}\n")

    def __str__(self):
        """The string representation of the book with buy and sell orders listed"""

        start_line = f"{self.ticker}:\n" if self.ticker else ""
        if not self.buy_orders and not self.sell_orders:
            return start_line + "No open orders."

        str_list = []
        if self.buy_orders:
            str_list.append("BUY ORDERS:")
            for orders in self.buy_orders.values():
                for order in orders:
                    str_list.append(self.PRINT_ORDER_FORMAT.format(order.price, order.quantity))
        if self.sell_orders:
            str_list.append("\nSELL ORDERS:" if str_list else "SELL ORDERS:")
            for orders in self.sell_orders.values():
                for order in orders:
                    str_list.append(self.PRINT_ORDER_FORMAT.format(order.price, order.quantity))

        return start_line + "\n".join(str_list)
