from unittest import TestCase

from order import Order
from order_book import OrderBook


class TestOrderBook(TestCase):

    def test_print_orders(self):
        orders = [Order(True, 10, 12.23)
            , Order(True, 20, 12.31)
            , Order(False, 5, 13.55)
            , Order(False, 5, 13.31)
            , Order(True, 30, 12.23)]

        book = OrderBook()
        for o in orders:
            book.process_order(o)

        # book.print_orders()
        expected_str = """Buy Side:
0) Price=12.31, Total units=20
1) Price=12.23, Total units=40
Sell Side:
0) Price=13.31, Total units=5
1) Price=13.55, Total units=5"""

        self.assertEqual(expected_str, str(book))


