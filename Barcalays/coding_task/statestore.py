from datetime import date
from typing import Dict, Generic, Optional

from base import StrategyState


class StateStore(Generic[StrategyState]):
    """
    A generic cache for strategy states.
    This class provides a pure caching mechanism for strategy states.
    It stores and retrieves computed states, and also tracks the version of the state by date.

    Type Parameters:
        StrategyState: The type of state object returned by the strategy

    Attributes:
        _cache: Internal dictionary mapping dates to cached states
        _cached_versions: Internal dictionary mapping dates to their cached versions
    """

    def __init__(self):
        """Initialize an empty StateStore."""
        self._cache: Dict[date, StrategyState] = {}
        self._cached_versions: Dict[date, int] = {}

    def get_state(self, target_date: date, version: int) -> Optional[StrategyState]:
        """
        Get the cached state for a specific date, if available and valid.
        This method checks the version of the cached state against the provided version.
        If versions differ, invalidates the target date and all subsequent dates dependent on it.

        Args:
            target_date: The date for which to get the cached state
            version: The current version of the target date from MarketData

        Returns:
            Optional[StrategyState]: The cached state if available and valid, None otherwise
        """
        if target_date not in self._cache:
            return None

        cached_version = self._cached_versions.get(target_date, 1)
        if cached_version == version:
            return self._cache.get(target_date)

        # Version mismatch - invalidate all dates >= target_date
        dates_to_remove = [cached_date for cached_date in self._cache.keys() if cached_date >= target_date]
        for date_to_remove in dates_to_remove:
            del self._cache[date_to_remove]
            if date_to_remove in self._cached_versions:
                del self._cached_versions[date_to_remove]

        return None

    def set_state(self, target_date: date, state: StrategyState, version: int) -> None:
        """
        Store a computed state in the cache along with its version.

        Args:
            target_date: The date for which to cache the state
            state: The computed state to cache
            version: The version of the target date from MarketData
        """
        if version < 1:
            raise ValueError(f"version must be >= 1, got {version}")

        self._cache[target_date] = state
        if version > 1:
            self._cached_versions[target_date] = version

    def has_state(self, target_date: date, version: int) -> bool:
        """
        Check if the cache has the state for a specific date and version.

        Args:
            target_date: The date for which to check the cached state
            version: The current version of the target date from MarketData

        Returns:
            bool: True if the state is cached, False otherwise
        """
        return target_date in self._cache and version == self._cached_versions.get(target_date, 1)