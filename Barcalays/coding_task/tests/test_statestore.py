from datetime import date
from dataclasses import dataclass

from statestore import StateStore


@dataclass(frozen=True)
class TestState:
    """Simple test state for StateStore tests."""
    value: float
    data: str


class TestStateStore:
    """Test suite for StateStore functionality."""

    def test_set_and_get_state(self):
        """Test basic set_state and get_state operations."""
        store = StateStore[TestState]()
        test_date = date(2023, 1, 1)
        test_state = TestState(value=100.0, data="test")
        version = 1

        assert not store.has_state(test_date, version)
        store.set_state(test_date, test_state, version)
        retrieved = store.get_state(test_date, version)
        assert retrieved is not None
        assert retrieved.value == 100.0
        assert retrieved.data == "test"

    def test_version_mismatch_invalidates(self):
        """Test that version mismatch invalidates target date and all subsequent dates."""
        store = StateStore[TestState]()

        dates = [
            date(2023, 1, 1),
            date(2023, 1, 2),
            date(2023, 1, 3),
            date(2023, 1, 4),
        ]

        # Set states for all dates with version 1
        for d in dates:
            store.set_state(d, TestState(value=float(d.day), data="test"), version=1)
            assert store.has_state(d, version=1)

        # Should invalidate update_date and all subsequent dates
        update_date = dates[1]
        assert store.get_state(update_date, version=2) is None
        assert not store.has_state(dates[2], version=1)
        assert not store.has_state(dates[3], version=1)

        # But previous date should still be cached
        assert store.has_state(dates[0], version=1)

    def test_get_state_returns_none_for_missing_date(self):
        """Test that get_state returns None for dates not in cache."""
        store = StateStore[TestState]()
        test_date = date(2023, 1, 1)

        assert store.get_state(test_date, version=1) is None

