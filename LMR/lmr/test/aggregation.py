from typing import NamedTuple, Set, Optional


class Pnl(NamedTuple):
    dailyPnl: float


class PortfolioPnl(NamedTuple):
    """
    Contains the pnl for the positions in the portfolio. Does not include pnl from sub-portfolios
    """

    portfolioId: int
    """The portfolio which this object refers to"""

    pnl: Pnl


class PortfolioInfo(NamedTuple):
    """
    Definition of a portfolio
    A portfolio may contain other portfolios, which are referred to by id.
    """

    id: int
    name: str
    subFolios: Optional[Set[int]] = set()


class TestData:

    @staticmethod
    def getTestPortfolios():
        """
        Creates a set of test portfolio data with this structure

        1 - Fund A
            2 - Macro
                4 - Europe
                5 - US
            3 - Quant
                6 - Asia
                7 - Europe
        8 - Fund B
            9 - Fixed Income
                10 - RV
                11 - Delta
                12 - Hedge
            13 - Fees

        :return:  A dummy portfolio structure
        """
        return [
            PortfolioInfo(1, "Fund A", set([2, 3])),
            PortfolioInfo(2, "Macro", set([4, 5])),
            PortfolioInfo(3, "Quant", set([6, 7])),
            PortfolioInfo(4, "Europe"),
            PortfolioInfo(5, "US"),
            PortfolioInfo(6, "Asia"),
            PortfolioInfo(7, "Europe"),
            PortfolioInfo(8, "Fund B", set([9, 13])),
            PortfolioInfo(9, "Fixed Income", set([10, 11, 12])),
            PortfolioInfo(10, "RV"),
            PortfolioInfo(11, "Delta"),
            PortfolioInfo(12, "Hedge"),
            PortfolioInfo(13, "Fees")
        ]

    @staticmethod
    def getTestPnlData():
        """
        :return: a list of PortfolioPnl items which give you the pnl for positions in that portfolio.
        Does not include pnl from sub portfolios
        """
        return [
            PortfolioPnl(1, Pnl(0)),
            PortfolioPnl(2, Pnl(1e6)),
            PortfolioPnl(3, Pnl(0)),
            PortfolioPnl(4, Pnl(1e5)),
            PortfolioPnl(5, Pnl(12313)),
            PortfolioPnl(6, Pnl(98860)),
            PortfolioPnl(7, Pnl(-780000)),
            PortfolioPnl(8, Pnl(0)),
            PortfolioPnl(9, Pnl(78988)),
            PortfolioPnl(10, Pnl(2613821)),
            PortfolioPnl(11, Pnl(-174588)),
            PortfolioPnl(12, Pnl(-2018906))
        ]
