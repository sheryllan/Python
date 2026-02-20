from typing import List, Set
from functools import cache
from lmr.test.aggregation import PortfolioPnl, PortfolioInfo


class PortfolioAggregator:
    """
    Aggregates portfolio PnL data and generates hierarchical reports
    """

    def __init__(self, portfolios: List[PortfolioInfo], pnl_data: List[PortfolioPnl]):
        self.portfolios = {p.id: p for p in portfolios}
        self.pnl_data = {p.portfolioId: p.pnl.dailyPnl for p in pnl_data}
        self.root_portfolios = self.find_root_portfolios()

    def find_root_portfolios(self) -> Set[int]:
        """Find portfolio IDs that are not sub-portfolios of any other portfolio"""
        root_portfolios = set(self.portfolios.keys())
        for portfolio in self.portfolios.values():
            root_portfolios.difference_update(portfolio.subFolios)
        return root_portfolios

    @cache
    def calculate_aggregated_pnl(self, portfolio_id: int) -> float:
        """
        Recursively calculate the aggregated PnL for a portfolio including all sub-portfolios
        """
        portfolio = self.portfolios[portfolio_id]
        total_pnl = self.pnl_data.get(portfolio_id, 0.0)
        if portfolio.subFolios:
            for sub_portfolio_id in portfolio.subFolios:
                total_pnl += self.calculate_aggregated_pnl(sub_portfolio_id)

        return total_pnl

    def print_portfolio_hierarchy(self, portfolio_id: int, indent_level: int = 0):
        """
        Recursively print the portfolio hierarchy with indentation and aggregated PnL
        """
        portfolio = self.portfolios[portfolio_id]
        aggregated_pnl = self.calculate_aggregated_pnl(portfolio_id)

        indent = "   " * indent_level
        print(f"{indent}{portfolio.name} - {aggregated_pnl}")

        if portfolio.subFolios:
            for sub_portfolio_id in sorted(portfolio.subFolios):
                self.print_portfolio_hierarchy(sub_portfolio_id, indent_level + 1)

    def generate_report(self):
        """
        Generate and print the complete portfolio hierarchy report
        """
        print("Complete portfolio hierarchy report:")
        for root_id in sorted(self.root_portfolios):
            self.print_portfolio_hierarchy(root_id)
            print()

