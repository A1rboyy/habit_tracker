import pytest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
print(sys.path)
from fastapi.testclient import TestClient
from application.main import app
from application.database import init_db
import application.analytics as analytics
from datetime import datetime, timedelta

@pytest.fixture(autouse=True)
def setup_db():
    # Reinitialize DB schema before every test
    init_db()

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Setup: initialize the database fresh before each test
    init_db()
    yield

def test_create_habit():
    # Data to create a habit
    habit_data = {
        "name": "Test Habit",
        "description": "Testing habit creation",
        "periodicity": "daily"
    }

    response = client.post("/habits/", json=habit_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == habit_data["name"]
    assert data["description"] == habit_data["description"]
    assert data["periodicity"] == habit_data["periodicity"]
    assert "id" in data

    # Verify habit actually exists via get
    habit_id = data["id"]
    get_response = client.get(f"/habits/periodicity/{habit_data['periodicity']}")
    assert get_response.status_code == 200
    habits = get_response.json()
    assert any(h["name"] == "Test Habit" for h in habits)

def test_delete_habit():
    # First create a habit to delete
    habit_data = {
        "name": "Habit to delete",
        "description": "Will be deleted",
        "periodicity": "weekly"
    }
    create_resp = client.post("/habits/", json=habit_data)
    habit_id = create_resp.json()["id"]

    # Delete the habit
    delete_resp = client.delete(f"/habits/{habit_id}")
    assert delete_resp.status_code == 204

    # Trying to delete again should return 404
    delete_resp_2 = client.delete(f"/habits/{habit_id}")
    assert delete_resp_2.status_code == 404

    # Trying to get habit should return empty (via periodicity listing)
    get_resp = client.get(f"/habits/periodicity/{habit_data['periodicity']}")
    habits = get_resp.json()
    assert all(h["id"] != habit_id for h in habits)

def iso_dates_from_days_ago(days_ago_list):
    """Helper: convert list of days ago to ISO date strings."""
    today = datetime.utcnow().date()
    return [(today - timedelta(days=d)).isoformat() for d in days_ago_list]


@pytest.mark.parametrize("dates,periodicity,expected", [
    ([], "daily", 0),
    ([], "weekly", 0),
    (iso_dates_from_days_ago([2, 1, 0]), "daily", 3),  # 3-day streak
    (iso_dates_from_days_ago([4, 3, 1]), "daily", 2),  # broken streak: 4-3 (2), 1 alone (1)
    (iso_dates_from_days_ago([21, 14, 7, 0]), "weekly", 4),  # 4 week streak
    (iso_dates_from_days_ago([21, 14, 0]), "weekly", 2),  # broken weekly streak
])
def test_longest_streak_for_habit(monkeypatch, dates, periodicity, expected):
    monkeypatch.setattr(analytics, "get_completions", lambda habit_id: dates)
    result = analytics.longest_streak_for_habit(1, periodicity)
    assert result == expected


def test_longest_streak_overall(monkeypatch):
    habits = [
        {"id": 1, "periodicity": "daily"},
        {"id": 2, "periodicity": "weekly"},
        {"id": 3, "periodicity": "daily"},
    ]

    monkeypatch.setattr(analytics, "get_all_habits", lambda: habits)

    # Provide different streaks per habit
    def fake_longest_streak_for_habit(habit_id, periodicity):
        return {1: 3, 2: 5, 3: 2}[habit_id]

    monkeypatch.setattr(analytics, "longest_streak_for_habit", fake_longest_streak_for_habit)

    result = analytics.longest_streak_overall()
    assert result == {"habit_id": 2, "streak": 5}


def test_longest_streak_overall_no_habits(monkeypatch):
    monkeypatch.setattr(analytics, "get_all_habits", lambda: [])
    result = analytics.longest_streak_overall()
    assert result == {"habit_id": None, "streak": 0}