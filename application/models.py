from pydantic import BaseModel, ConfigDict, Field, constr
from datetime import datetime
from enum import Enum
from typing import Optional

class Periodicity(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"

# ─────────  objects coming *into* the system ─────────
class HabitCreate(BaseModel):
    name: str
    description: Optional[str] = None
    periodicity: Periodicity


# ─────────  objects stored / returned  ─────────
class Habit(HabitCreate):
    id: int
    created_at: datetime = Field(..., description="UTC timestamp")

    model_config = ConfigDict(from_attributes=True)


class Completion(BaseModel):
    id: int
    habit_id: int
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)