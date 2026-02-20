
import pandas as pd
import logging



COLUMNS = ['Ticker','TradeValueUSD','PriceUSD']
COL_TICKER = 'Ticker'
COL_TRADE_VALUE_USD = 'TradeValueUSD'
COL_PRICE_USD = 'PriceUSD'
COL_NET_TRADE_VALUE = 'NetTradeValue'
COL_QUANTITY = 'Quantity'
COL_VWAP = 'VWAP'
COL_PRICE_DEVIATION_PCT = 'PriceDeviationPct'


logging.basicConfig()


def read_trade_file(csv_file: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(csv_file)
        logging.info(f"Successfully loaded {len(df)} trades from {csv_file}")
        # Clean column headers (remove any whitespace)
        # df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        logging.error(f"Error: Could not find file {csv_file}")
    except Exception as e:
        logging.error(f"Error reading file: {e}")
        raise



def get_net_postions(df: pd.DataFrame) -> pd.DataFrame:
    net_positions = df.groupby(COL_TICKER)[COL_TRADE_VALUE_USD].sum().reset_index()
    net_positions.columns = [COL_TICKER, COL_NET_TRADE_VALUE]
    return net_positions


def get_largest_trades(csv_file: str, n: int) -> None:
    """
    Analyze trading data to find largest net buy and sell positions.

    Args:
        csv_file (str): Path to the CSV file containing trade data
        n: the number of largest
    """

    df = read_trade_file(csv_file)

    net_positions = df.groupby(COL_TICKER)[COL_TRADE_VALUE_USD].sum().reset_index()
    net_positions.columns = [COL_TICKER, COL_NET_TRADE_VALUE]

    sorted_net_positions = net_positions.sort_values(COL_NET_TRADE_VALUE, ascending=False)
    # if the net trade value is zero, take it as a buy
    net_buys = sorted_net_positions[sorted_net_positions[COL_NET_TRADE_VALUE] >= 0]
    net_sells = sorted_net_positions[sorted_net_positions[COL_NET_TRADE_VALUE] < 0]

    top_n_buys = net_buys.head(n)
    top_n_sells = net_sells.tail(n).iloc[::-1]

    print_largest_trades(top_n_buys, 'buy')
    print('\n')
    print_largest_trades(top_n_sells, 'sell')



def print_largest_trades(df: pd.DataFrame, trade_type: str):
    n = len(df)
    header_string = f"{'Rank':<4} {'Ticker':<20} {'Net Trade Value (USD)':<20}"

    print(f"Top {n} largest net {trade_type} positions")
    print(header_string)
    for i, (_, row) in enumerate(df.iterrows(), 1):
        print(f"{i:<4} {row[COL_TICKER]:<20} ${row[COL_NET_TRADE_VALUE]:>18,.2f}")

    #
    # print()
    # print("=" * 60)
    # print("SUMMARY STATISTICS")
    # print("=" * 60)
    #
    # total_gross_trading = df['TradeValueUSD'].abs().sum()
    # total_net_trading = df['TradeValueUSD'].sum()
    # total_buy_value = net_buys['NetTradeValue'].sum()
    # total_sell_value = net_sells['NetTradeValue'].sum()
    #
    # print(f"Total Gross Trading Volume: ${total_gross_trading:,.2f}")
    # print(f"Total Net Trading Volume: ${total_net_trading:,.2f}")
    # print(f"Total Net Buys: ${total_buy_value:,.2f}")
    # print(f"Total Net Sells: ${total_sell_value:,.2f}")
    # print(f"Number of Unique Tickers: {len(net_positions)}")
    # print(f"Number of Individual Trades: {len(df)}")


def compliance_analysis(csv_file: str, n: int):
    """
    Analyze trades for compliance with best execution policy by calculating VWAP
    and identifying trades with largest price deviations.

    Args:
        csv_file (str): Path to the CSV file containing trade data
    """
    df = read_trade_file(csv_file)
    df[COL_QUANTITY] = (df[COL_TRADE_VALUE_USD] / df[COL_PRICE_USD]).abs()

    # VWAP = SUM(priceUSD * quantity) / SUM(quantity)
    gb_ticker = df.groupby(COL_TICKER)
    quantities = gb_ticker[COL_QUANTITY]
    # prices = gb_ticker[COL_PRICE_USD]
    qty_summed = quantities.sum()
    net_trade_values = gb_ticker[COL_TRADE_VALUE_USD].sum()
    vwap_df = (net_trade_values.abs() / qty_summed).reset_index()
    vwap_df.columns = [COL_TICKER, COL_VWAP]
    df_with_vwap = df.merge(vwap_df, on=COL_TICKER, how='left')

    # Calculate percentage deviation from VWAP
    vwaps = df_with_vwap[COL_VWAP]
    prices = df_with_vwap[COL_PRICE_USD]
    df_with_vwap[COL_PRICE_DEVIATION_PCT] = (prices - vwaps) / vwaps * 100
    df_with_vwap['dd'] = df_with_vwap[COL_PRICE_DEVIATION_PCT].abs()
    df_top_n_deviations = df_with_vwap.nlargest(n, 'dd')

    print_largest_vwap_deviation(df_top_n_deviations)

    return df_with_vwap, vwap_df


def print_largest_vwap_deviation(df: pd.DataFrame) -> None:
    n = len(df)
    print(f"Top {n} trades with largest VWAP deviation")
    print(f"{'Rank':<4} {'Ticker':<15} {'Trade Price':<12} {'VWAP':<12} {'Deviation %':<12} {'Trade Value':<15}")

    for i, (_, row) in enumerate(df.iterrows(), 1):
        deviation_sign = "+" if row[COL_PRICE_DEVIATION_PCT] >= 0 else ""
        print(
            f"{i:<4} {row[COL_TICKER]:<15} ${row[COL_PRICE_USD]:<11.3f} ${row[COL_VWAP]:<11.3f} {deviation_sign}{row[COL_PRICE_DEVIATION_PCT]:<11.2f}% ${row[COL_TRADE_VALUE_USD]:<14,.2f}")




if __name__ == "__main__":
    # Run the analysis
    csv_filename = "../tradesUSD copy.csv"

    compliance_analysis(csv_filename, 10)
    # get_largest_trades(csv_filename, 10)