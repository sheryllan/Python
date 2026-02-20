## Order Book

### Core Classes

- Order: Represents individual buy/sell orders
- SingleOrderBook: The order book implementation for a single contract with matching logic
- MultiOrderBook: The order book implementation for multiple contracts with 

### Requirements

- Python 3.7 or higher
- No external dependencies required

### Installation & Usage

#### Using the SingleOrderBook Class
```python
from single_order_book import SingleOrderBook

orders = [
            {"type": "BUY", "price": 102, "quantity": 5},
            {"type": "SELL", "price": 104, "quantity": 2},
            {"type": "BUY", "price": 101, "quantity": 3},
            {"type": "SELL", "price": 103, "quantity": 4}
        ]

book = SingleOrderBook(orders)

# Matched order will be printed to stdout as well as the book after each match
book.add_orders([{"type": "SELL", "price": 102, "quantity": 1}])
```

```
__Expected Output__:

Match: BUY 5@102 with SELL 1@102

BUY ORDERS:
Price: 102, Quantity: 4
Price: 101, Quantity: 3

SELL ORDERS:
Price: 103, Quantity: 4
Price: 104, Quantity: 2

```


#### Using the MultiOrderBook Class
```python
from multi_order_book import MultiOrderBook

orders = [
            {"type": "BUY", "price": 1500, "quantity": 2, "contract": "GCQ4 Comdty"},
            {"type": "SELL", "price": 1500, "quantity": 3, "contract": "GCZ4 Comdty"},
        ]

book = MultiOrderBook()

# Matched order will be printed to stdout as well as the book after each match 
# with an indication of which contract
book.add_orders(orders)

# Display current state
print(str(book))

# View a specific contract book for given expiration
contract_book = book.view_contract_book("GC", (2024, 8))
print(str(contract_book))
```

```
__Expected Output__:

GCQ4 Comdty:
BUY ORDERS:
Price: 1500, Quantity: 2

GCZ4 Comdty:
SELL ORDERS:
Price: 1500, Quantity: 3

GCQ4 Comdty:
BUY ORDERS:
Price: 1500, Quantity: 2

```