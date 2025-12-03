from datetime import date
from typing import List
import pandas as pd

from marketdata import MarketData
from rule import EqualWeightStrategy
from runner import get_states

def compute_and_check(strategy: EqualWeightStrategy, final_date: str, expected: float):
    final_level = strategy.compute_state(date.fromisoformat(final_date)).index_level
    assert round(final_level, 6) == expected, f"Index level to 6dp on {final_date} should be {expected}, got {final_level}"

def get_states_and_check(strategy: EqualWeightStrategy, from_date: str, to_date: str, expected: List[float]):
    states = get_states(strategy, date.fromisoformat(from_date), date.fromisoformat(to_date)).values()
    levels = [round(state.index_level, 6) for state in states]
    assert levels == expected

def initialise() -> EqualWeightStrategy:
    md = MarketData('sample_prices.csv')
    strategy = EqualWeightStrategy(
        md=md,
        basket=["SPX", "SX5E", "HSI"],
        seed_date=date.fromisoformat("2023-01-02"),
        calendar=md.get_calendar(),
        initial_index_level=100,
    )
    return strategy


def test_strategy_calculation():
    strategy = initialise()
    compute_and_check(strategy, "2023-01-03", 100.066461)
    compute_and_check(strategy, "2023-01-31", 93.227305)
    compute_and_check(strategy, "2023-02-01", 92.277544)
    compute_and_check(strategy, "2023-05-19", 92.441678)

def test_calculate_range():
    strategy = initialise()
    get_states_and_check(strategy, "2023-02-05", "2023-02-08", [94.098372, 93.541086, 92.601076])


def test_compute_state_against_expected_output():
    """Test that compute_state results match expected_output.csv exactly."""
    # Load expected output
    expected_file = 'expected_output.csv'
    expected_df = pd.read_csv(expected_file)
    expected_df['date'] = pd.to_datetime(expected_df['date']).dt.date

    strategy = initialise()

    # Compute states for all dates in expected output
    computed_states = get_states(strategy, None, date.fromisoformat("2023-06-29"))
    computed_df = pd.DataFrame([
        {'date': d, 'index_level': state.index_level}
        for d, state in computed_states.items()
    ])
    computed_df['date'] = pd.to_datetime(computed_df['date']).dt.date

    expected_df = expected_df.sort_values('date').reset_index(drop=True)
    computed_df = computed_df.sort_values('date').reset_index(drop=True)

    pd.testing.assert_frame_equal(
        expected_df,
        computed_df,
        check_exact=False,
        atol=1e-10,
        rtol=0
    )


def test_compute_state_cascade_invalidation():
    """Test that updating a price invalidates all subsequent cached states."""
    strategy = initialise()
    md = strategy.md

    # Compute states for a range of dates
    dates = [
        date.fromisoformat("2023-01-03"),
        date.fromisoformat("2023-01-04"),
        date.fromisoformat("2023-01-05"),
    ]
    original_states = {d: strategy.compute_state(d) for d in dates}

    # Update price for middle date
    update_date = dates[1]
    original_price = md.get(update_date, "SPX")
    md.update_price(update_date, "SPX", original_price * 1.1)

    # Recompute - should get different results for update_date and later dates, but not for earlier dates
    updated_state_earlier = strategy.compute_state(dates[0])
    updated_state_middle = strategy.compute_state(update_date)
    updated_state_later = strategy.compute_state(dates[2])
    assert updated_state_earlier.index_level == original_states[dates[0]].index_level
    assert updated_state_middle.index_level != original_states[update_date].index_level
    assert updated_state_later.index_level != original_states[dates[2]].index_level

    # Test for an update for another date
    changed_states = {
        dates[0]: updated_state_earlier,
        dates[1]: updated_state_middle,
        dates[2]: updated_state_later
    }
    update_date = dates[2]
    original_price = md.get(update_date, "SPX")
    md.update_price(update_date, "SPX", original_price * 1.1)
    updated_state = strategy.compute_state(update_date)
    updated_state_prev0 = strategy.compute_state(dates[0])
    updated_state_prev1 = strategy.compute_state(dates[1])

    assert updated_state.index_level != changed_states[update_date].index_level
    assert updated_state_prev0.index_level == changed_states[dates[0]].index_level
    assert updated_state_prev1.index_level == changed_states[dates[1]].index_level



