import unittest
import sys
from io import StringIO

from multi_order_book import MultiOrderBook


class TestMultiOrderBook(unittest.TestCase):
    """Test Stage 3: Order book with futures contracts functionality."""

    def test_contract_separation(self):
        """Test that different contracts are kept separate."""
        orders = [
            {"type": "BUY", "price": 1500, "quantity": 2, "contract": "GCQ4 Comdty"},
            {"type": "SELL", "price": 1500, "quantity": 3, "contract": "GCZ4 Comdty"},
            {"type": "BUY", "price": 1500, "quantity": 1},  # No contract will have "Unknown" ticker
        ]

        book = MultiOrderBook()
        book.add_orders(orders)

        gcq4_orders = book.contracts["GCQ4 Comdty"]
        gcz4_orders = book.contracts["GCZ4 Comdty"]
        basic_orders = book.contracts["Unknown"]

        self.assertEqual(len(gcq4_orders.buy_orders), 1)
        self.assertFalse(gcq4_orders.sell_orders)
        self.assertEqual(gcq4_orders.buy_orders[1500][0].quantity, 2)

        self.assertEqual(len(gcz4_orders.sell_orders), 1)
        self.assertFalse(gcz4_orders.buy_orders)
        self.assertEqual(gcz4_orders.sell_orders[1500][0].quantity, 3)

        self.assertEqual(len(basic_orders.buy_orders), 1)
        self.assertFalse(basic_orders.sell_orders)
        self.assertEqual(basic_orders.buy_orders[1500][0].quantity, 1)

    def test_same_contract_matching(self):
        """Test that orders match within the same contract."""
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        book = MultiOrderBook()
        book.add_orders([
            {"type": "BUY", "price": 1500, "quantity": 2, "contract": "GCQ4 Comdty"},
            {"type": "SELL", "price": 1500, "quantity": 2, "contract": "GCQ4 Comdty"},
            {"type": "BUY", "price": 1550, "quantity": 3, "contract": "GCZ4 Comdty"},
            {"type": "SELL", "price": 1550, "quantity": 1, "contract": "GCZ4 Comdty"}
        ])

        sys.stdout = old_stdout
        output = captured_output.getvalue().strip()

        self.assertEqual("""Match: BUY 2@1500 with SELL 2@1500 on GCQ4 Comdty

GCQ4 Comdty:
No open orders.

Match: BUY 3@1550 with SELL 1@1550 on GCZ4 Comdty

GCZ4 Comdty:
BUY ORDERS:
Price: 1550, Quantity: 2""", output)

        gcq4_orders = book.contracts["GCQ4 Comdty"]
        gcz4_orders = book.contracts["GCZ4 Comdty"]
        self.assertFalse(gcq4_orders.buy_orders)
        self.assertFalse(gcq4_orders.sell_orders)
        self.assertEqual(gcz4_orders.buy_orders[1550][0].quantity, 2)
        self.assertFalse(gcz4_orders.sell_orders)

    def test_view_contract_book(self):
        """Test to view the contract book for a given expiration"""
        book = MultiOrderBook()
        book.add_orders([
            {"type": "BUY", "price": 1500, "quantity": 2, "contract": "GCQ4 Comdty"},
            {"type": "SELL", "price": 1500, "quantity": 2, "contract": "GCQ4 Comdty"},
            {"type": "BUY", "price": 1550, "quantity": 3, "contract": "GCZ4 Comdty"},
            {"type": "SELL", "price": 1550, "quantity": 1, "contract": "GCZ4 Comdty"}
        ])

        expected = """GCZ4 Comdty:
BUY ORDERS:
Price: 1550, Quantity: 2"""

        actual = book.view_contract_book("GC", (2024, 12))
        self.assertEqual(expected, actual)

