
class Order:
    def __init__(self, is_buy: bool, qty: int, price: float):
        self.is_buy = is_buy
        self.qty = qty
        self.price = price

    def update_qty(self, new_qty: int):
        self.qty += new_qty



