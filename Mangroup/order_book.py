from collections import OrderedDict
from order import Order


class OrderBook:
    def __init__(self):
        self.buy_orders = {}
        self.sell_orders = {}

    def process_order(self, order: Order):
        new_order = order
        if order.is_buy:
            if order.price in self.buy_orders:
                new_order = self.buy_orders[order.price]
                new_order.update_qty(order.qty)
            self.buy_orders[order.price] = new_order
        else:
            if order.price in self.sell_orders:
                new_order = self.sell_orders[order.price]
                new_order.update_qty(order.qty)
            self.sell_orders[order.price] = new_order

    def print_orders(self):
        self.buy_orders = OrderedDict(sorted(self.buy_orders.items(), key=lambda x: x[1].price, reverse=True))
        self.sell_orders = OrderedDict(sorted(self.sell_orders.items(), key=lambda x: x[1].price))

        output = ['Buy Side:']
        for i, order in enumerate(self.buy_orders.values()):
            output.append(f'{i}) Price={order.price}, Total units={order.qty}')

        output.append('Sell Side:')
        for i, order in enumerate(self.sell_orders.values()):
            output.append(f'{i}) Price={order.price}, Total units={order.qty}')

        output_str = '\n'.join(output)
        print(output_str)
        return output_str

    def __str__(self):
        return self.print_orders()

    def __repr__(self):
        return self.__str__()




