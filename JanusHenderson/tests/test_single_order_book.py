import unittest
import sys
from io import StringIO

from single_order_book import SingleOrderBook


class TestSingleOrderBook(unittest.TestCase):
    def setUp(self):
        """Set up test order book with initial orders."""

        orders = [
            {"type": "BUY", "price": 102, "quantity": 5},
            {"type": "SELL", "price": 104, "quantity": 2},
            {"type": "BUY", "price": 101, "quantity": 3},
            {"type": "SELL", "price": 103, "quantity": 4}
        ]

        self.book = SingleOrderBook(orders)

    def test_stage1_basic_order_book(self):
        """Test Stage 1: print basic order book."""

        expected_output = """BUY ORDERS:
Price: 102, Quantity: 5
Price: 101, Quantity: 3

SELL ORDERS:
Price: 103, Quantity: 4
Price: 104, Quantity: 2"""

        actual_output = str(self.book)
        self.assertEqual(expected_output, actual_output)

    def test_stage2_exact_price_match(self):
        """Test Stage 2: test matching at exact price."""
        # Capture output to check for match message
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        self.book.add_orders([{"type": "SELL", "price": 102, "quantity": 1}])

        sys.stdout = old_stdout
        output = captured_output.getvalue().strip()

        # Check match was printed
        self.assertEqual("""Match: BUY 5@102 with SELL 1@102

BUY ORDERS:
Price: 102, Quantity: 4
Price: 101, Quantity: 3

SELL ORDERS:
Price: 103, Quantity: 4
Price: 104, Quantity: 2""", output)

        buy_orders = list(self.book.buy_orders.values())
        self.assertEqual(buy_orders[0][0].price, 102)
        self.assertEqual(buy_orders[0][0].quantity, 4)

    def test_stage2_buy_higher_than_sell_price(self):
        """Test Stage 2: test buy order with price higher than sell order."""
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        self.book.add_orders([
            {"type": "BUY", "price": 104, "quantity": 2},
            {"type": "BUY", "price": 103.5, "quantity": 1}
        ])

        sys.stdout = old_stdout
        output = captured_output.getvalue()

        self.assertIn("BUY 2@104 with SELL 4@103", output)
        self.assertIn("BUY 1@103.5 with SELL 2@103", output)

        # Check sell order at 103 was partially filled
        remaining_103_orders = self.book.sell_orders[103]
        self.assertEqual(remaining_103_orders[0].quantity, 1)

    def test_stage2_partial_fill(self):
        """Test Stage 2: test partial fill when buy sell quantities are imbalanced."""
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        # Add large buy order
        self.book.add_orders([{"type": "BUY", "price": 105, "quantity": 10}])

        sys.stdout = old_stdout
        output = captured_output.getvalue()

        self.assertIn("BUY 10@105 with SELL 4@103", output)
        self.assertIn("BUY 6@105 with SELL 2@104", output)

        # sell_orders should be empty
        self.assertFalse(self.book.sell_orders)

        buy_orders = list(self.book.buy_orders.values())
        self.assertEqual(buy_orders[0][0].price, 105)
        self.assertEqual(buy_orders[0][0].quantity, 4)

    def test_stage2_multiple_orders_at_the_same_price(self):
        """Test Stage 2: test matching orders at the same price level"""
        old_stdout = sys.stdout
        sys.stdout = captured_output = StringIO()

        self.book.add_orders([
            {"type": "SELL", "price": 104, "quantity": 4},
            {"type": "BUY", "price": 105, "quantity": 10}
        ])

        sys.stdout = old_stdout
        output = captured_output.getvalue().strip()

        expected = """Match: BUY 10@105 with SELL 4@103

BUY ORDERS:
Price: 105, Quantity: 6
Price: 102, Quantity: 5
Price: 101, Quantity: 3

SELL ORDERS:
Price: 104, Quantity: 2
Price: 104, Quantity: 4

Match: BUY 6@105 with SELL 2@104

BUY ORDERS:
Price: 105, Quantity: 4
Price: 102, Quantity: 5
Price: 101, Quantity: 3

SELL ORDERS:
Price: 104, Quantity: 4

Match: BUY 4@105 with SELL 4@104

BUY ORDERS:
Price: 102, Quantity: 5
Price: 101, Quantity: 3"""
        self.assertEqual(expected, output)



