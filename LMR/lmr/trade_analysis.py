import csv
from typing import List, Dict, Tuple
from collections import defaultdict
from math import isclose

import logging


logger = logging.getLogger(__name__)

COL_TICKER = 'Ticker'
COL_TRADE_VALUE_USD = 'TradeValueUSD'
COL_PRICE_USD = 'PriceUSD'


CSV_COLUMNS = [
    COL_TICKER,
    COL_TRADE_VALUE_USD,
    COL_PRICE_USD
]


class TradeRecord:
    """
    Represents a single trade record
    """

    def __init__(self, ticker: str, trade_value_usd: float, price_usd: float):
        self.ticker = ticker
        self.trade_value_usd = trade_value_usd
        self.price_usd = price_usd

        # Assume a floating point number is valid for quantity
        self.quantity = abs(trade_value_usd / price_usd) if not isclose(price_usd, 0) else 0


class TradeAggregate:
    """
    Represents aggregate information about trades
    """

    def __init__(self):
        self.net_trade_value = 0.
        self.total_quantity = 0.
        self.trades = []

    @property
    def vwap(self):
        # VWAP = sum(price * quantity) / sum(quantity)
        abs_trade_value_sum = sum(abs(trade.trade_value_usd) for trade in self.trades)
        return abs_trade_value_sum / self.total_quantity if not isclose(self.total_quantity, 0) else 0

    def add_trade(self, trade: TradeRecord):
        self.net_trade_value += trade.trade_value_usd
        self.total_quantity += trade.quantity
        self.trades.append(trade)


class TradeRecordEnriched(TradeRecord):
    """
    Represents a trade record enriched with VWAP and price deviation
    """

    def __init__(self, trade: TradeRecord, vwap: float):
        super().__init__(trade.ticker, trade.trade_value_usd, trade.price_usd)
        self.vwap = vwap
        self.price_deviation_pct = ((trade.price_usd - vwap) / vwap * 100) if not isclose(vwap, 0) else 0



def parse_trades_csv(filename: str) -> List[TradeRecord]:
    """
    Parse the trades CSV file
    """
    trades = []
    try:
        with open(filename, 'r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            missing_columns = [col for col in CSV_COLUMNS if col not in reader.fieldnames]
            if missing_columns:
                raise ValueError(f"Missing required columns: {missing_columns}")

            line_number = 1
            for row in reader:
                line_number += 1

                try:
                    ticker = row[COL_TICKER].strip()
                    trade_value_usd = float(row[COL_TRADE_VALUE_USD].strip())
                    price_usd = float(row[COL_PRICE_USD].strip())

                    trade = TradeRecord(ticker, trade_value_usd, price_usd)
                    trades.append(trade)

                except ValueError as e:
                    logger.error(f"Warning: Skipping line {line_number} due to data conversion error: {e}")
                    logger.error(f"  Row data: {row}")
                    continue
                except KeyError as e:
                    logger.error(f"Warning: Skipping line {line_number} due to missing column: {e}")
                    continue

    except FileNotFoundError:
        logger.error(f"Error: Could not find file '{filename}'")
        raise
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        raise

    logging.info(f"Successfully parsed {len(trades)} trade records")
    return trades


def aggregate_trades_by_ticker(trades: List[TradeRecord]) -> Dict[str, TradeAggregate]:
    """
    Aggregate trades by ticker to calculate net positions and other metrics
    """
    trade_aggregates = defaultdict(lambda: TradeAggregate())
    for trade in trades:
        trade_aggregates[trade.ticker].add_trade(trade)

    return trade_aggregates


def get_largest_positions(ticker_data: Dict[str, TradeAggregate], n: int = 10):
    """
    Get the largest net buy and sell positions
    """
    positions = [(ticker, data.net_trade_value) for ticker, data in ticker_data.items()]
    positions.sort(key=lambda x: x[1], reverse=True)

    buys = [(ticker, value) for ticker, value in positions if value > 0][:n]
    sells = [(ticker, value) for ticker, value in positions if value < 0][:-n-1:-1]

    return buys, sells


def print_largest_positions(positions: List[Tuple[str, float]], trade_type: str):
    """
    Print out the largest net buy and sell positions
    """
    n = len(positions)
    header_string = f"{'Rank':<5} {'Ticker':<20} {'Net Trade Value (USD)':<20}"

    print(f"Top {n} largest net {trade_type} positions:")
    print(header_string)

    rank = 1
    for i, (ticker, value) in enumerate(positions, 1):
        # Trades with the same net position should be of the same rank
        last_i = (i - 2) if i > 1 else 0
        rank = rank if value == positions[last_i][1] else i
        print(f"{rank:<5} {ticker:<20} {value:<20,.2f}")

    print("\n")


def generate_position_report(trades: List[TradeRecord], n: int = 10):
    """
    Generate a report of the net positions
    """
    trade_aggregates = aggregate_trades_by_ticker(trades)
    buys, sells = get_largest_positions(trade_aggregates, n)
    print_largest_positions(buys, 'buy')
    print_largest_positions(sells, 'sell')


def get_vwap_deviations(trades: List[TradeRecord], ticker_data: Dict[str, TradeAggregate], n: int = 10) -> List[TradeRecordEnriched]:
    """
    Get enriched trades with VWAP and price deviation
    """
    price_deviations: List[TradeRecordEnriched] = []
    for trade in trades:
        vwap = ticker_data[trade.ticker].vwap
        enriched_trade = TradeRecordEnriched(trade, vwap)
        price_deviations.append(enriched_trade)

    # Sort the trades by absolute value of price deviation
    price_deviations.sort(key=lambda x: abs(x.price_deviation_pct), reverse=True)
    return price_deviations[:n]


def print_largest_vwap_deviation(trades: List[TradeRecordEnriched]) -> None:
    """
    Print out trades with the largest VWAP deviation in price
    """
    n = len(trades)
    print(f"Top {n} trades with largest VWAP deviation in price:")
    print(f"{'Rank':<5} {'Ticker':<17} {'Trade Price':<15} {'VWAP':<15} {'Deviation(%)':<15} {'Trade Value':<15}")

    rank = 1
    for i, trade in enumerate(trades, 1):
        deviation_sign = "+" if trade.price_deviation_pct >= 0 else "-"
        # Trades with the same absolute price deviation should be of the same rank
        last_i = (i - 2) if i > 0 else 0
        rank = rank if abs(trade.price_deviation_pct) == abs(trades[last_i].price_deviation_pct) else i
        print(
            f"{rank:<5} {trade.ticker:<17} ${trade.price_usd:<14.3f} ${trade.vwap:<14.3f} "
            f"{deviation_sign}{trade.price_deviation_pct:<14.2f} ${trade.trade_value_usd:<15,.2f}")

    print("\n")


def generate_compliance_report(trades: List[TradeRecord], n: int = 10) -> None:
    """
    Generate a report for compliance
    """
    trade_aggregates = aggregate_trades_by_ticker(trades)
    price_deviations = get_vwap_deviations(trades, trade_aggregates, n)
    print_largest_vwap_deviation(price_deviations)




