from lmr.trade_analysis import parse_trades_csv, generate_position_report, generate_compliance_report


def test_generate_position_report():
    csv_filename = "../tradesUSD.csv"
    data = parse_trades_csv(csv_filename)
    generate_position_report(data)


def test_generate_compliance_report():
    csv_filename = "../tradesUSD.csv"
    data = parse_trades_csv(csv_filename)
    generate_compliance_report(data)
