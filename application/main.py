from typing import List

from fastapi import FastAPI, HTTPException, status

from .database import init_db
from . import crud, analytics, models
from fastapi import Query, Path
from datetime import datetime, timedelta

app = FastAPI(title="Habit Tracker API")

_PREDEFINED = [
    {"name": "Drink 2l water",    "desc": "Hydrate properly",            "period": "daily"},
    {"name": "Meditate 10 min",   "desc": "Mindfulness session",         "period": "daily"},
    {"name": "Read 20 pages",     "desc": "Deep reading time",           "period": "daily"},
    {"name": "Grocery shopping",  "desc": "Restock fridge & pantry",     "period": "weekly"},
    {"name": "Weekly review",     "desc": "Plan upcoming week & reflect","period": "weekly"},
]

def _seed_db():
    """
    Create the five habits and insert 30 days of backdated completions.
    """
    existing = {row[1]: row[0] for row in crud.get_all_habits()}  # name → id
    today = datetime.utcnow().date()

    for habit in _PREDEFINED:
        # 1) Create habit if it doesn’t exist yet
        habit_id = existing.get(habit["name"])
        if habit_id is None:
            habit_id = crud.create_habit(habit["name"], habit["desc"], habit["period"])
        else:
            continue

        # 2) Back‑fill completions for the last 30 days
        if habit["period"] == "daily":
            dates = [today - timedelta(days=i) for i in range(30)]
        else:  # weekly: mark once every 7 days
            dates = [today - timedelta(days=i) for i in range(0, 30, 7)]

        for d in dates:
            crud.insert_completion_at(habit_id, datetime.combine(d, datetime.min.time()))

@app.on_event("startup")
def on_startup():
    init_db()
    _seed_db()  


# ------------------------------ Habit CRUD ---------------------------------

@app.post("/habits/", response_model=models.Habit,status_code=status.HTTP_201_CREATED)
def create_habit(Habit: models.HabitCreate):
    """
    Creating a new habit with name, description and Periodicity
    """
    habit_id = crud.create_habit(**Habit.model_dump())
    row = crud.get_habit_by_id(habit_id)
    return models.Habit.model_validate(dict(row))


@app.get("/habits/periodicity/{periodicity}", response_model=List[dict])
def list_habits_by_periodicity(
    periodicity: models.Periodicity = Path(..., description="daily or weekly"),
):
    """
    Return all habits that have the specified periodicity.

    • GET /habits/periodicity/daily
    """
    rows = crud.get_habits_by_periodicity(periodicity)
    return [dict(r) for r in rows]


@app.delete("/habits/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(habit_id: int):
    """
    Deleting a habit by id
    """
    if not crud.get_habit_by_id(habit_id):
        raise HTTPException(status_code=404, detail="Habit not found")
    crud.delete_habit(habit_id)
    return None


# ------------------------------- Completions -------------------------------

@app.post("/habits/{habit_id}/complete", status_code=status.HTTP_201_CREATED)
def complete_habit(habit_id: int):
    """
    Completing a habit by id and storing the correct timestamp
    """
    if not crud.get_habit_by_id(habit_id):
        raise HTTPException(status_code=404, detail="Habit not found")
    crud.complete_habit(habit_id)
    return {"message": "Habit completed."}


# ------------------------------- Analytics ---------------------------------

@app.get("/analytics/longest-streak")
def get_longest_streak():
    """
    Return the habit ID and length of the longest streak among all habits.
    """
    return analytics.longest_streak_overall()


@app.get("/analytics/{habit_id}/longest-streak")
def get_longest_streak_for_habit(habit_id: int):
    """
    Return the habit id and lenght of streak for a specific habit.
    """
    habit = crud.get_habit_by_id(habit_id)
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    streak = analytics.longest_streak_for_habit(habit_id, habit[3])
    return {"habit_id": habit_id, "streak": streak}