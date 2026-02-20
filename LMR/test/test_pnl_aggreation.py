from lmr.test.aggregation import TestData
from lmr.pnl_aggreation import PortfolioAggregator


def test_generate_portfolio_report():
    portfolios = TestData.getTestPortfolios()
    pnl_data = TestData.getTestPnlData()

    aggregator = PortfolioAggregator(portfolios, pnl_data)
    aggregator.generate_report()

