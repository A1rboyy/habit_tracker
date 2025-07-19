from datetime import datetime, timedelta
from functools import reduce
from typing import Dict, Tuple

from .crud import get_all_habits, get_completions


# ---------------------------------------------------------------------------
# Helper to compute streak for a single ordered list of datetime objects

def _compute_streak(dates, delta_fn):
    if not dates:
        return 0
    streak = max_streak = 1
    for prev, curr in zip(dates, dates[1:]):
        if delta_fn(curr - prev):
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 1
    return max_streak


# ---------------------------------------------------------------------------
# Public API

def longest_streak_for_habit(habit_id: int, periodicity: str) -> int:
    """Return the longest streak length for a given habit, respecting periodicity."""
    raw_dates = get_completions(habit_id)
    if not raw_dates:
        return 0

    # Parsedates
    completed_dates = [datetime.fromisoformat(s) for s in raw_dates]

    if periodicity == "daily":
        # Keep only one entry per calendar day
        unique_periods = sorted({dt.date() for dt in completed_dates})
        # Delta is 1 day between entries
        within_period = lambda d: d <= timedelta(days=1)

    elif periodicity == "weekly":
        # Keep only one entry per ISO week
        unique_periods = sorted({(dt.isocalendar().year, dt.isocalendar().week) for dt in completed_dates})
        # Convert to pseudo-dates so we can compare
        unique_periods = [datetime.strptime(f'{y}-W{w}-1', "%G-W%V-%u").date() for y, w in unique_periods]
        within_period = lambda d: d <= timedelta(weeks=1)

    return _compute_streak(unique_periods, within_period)


def longest_streak_overall() -> Dict[str, int]:
    """Return the habit_id and length of the longest streak among all habits."""
    habits = get_all_habits()
    if not habits:
        return {"habit_id": None, "streak": 0}

    best = {"habit_id": None, "streak": 0}
    for habit in habits:
        habit_id = habit["id"]
        periodicity = habit["periodicity"]
        streak = longest_streak_for_habit(habit_id, periodicity)
        if streak > best["streak"]:
            best = {"habit_id": habit_id, "streak": streak}

    return best