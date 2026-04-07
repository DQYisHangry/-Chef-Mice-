from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.models.meal_plan import MealPlanStatus, MealSlot


class MealAssignment(BaseModel):
    """One recipe assigned to one slot on one day."""
    date: date
    slot: MealSlot
    recipe_id: str
    recipe_name: str
    servings: int


class PlanRequest(BaseModel):
    """User-facing input to trigger the planning agent."""
    days: Annotated[int, Field(ge=1, le=14)] = 5
    meals_per_day: list[MealSlot] = Field(default=[MealSlot.dinner])
    cuisine_override: list[str] = Field(default_factory=list)
    extra_constraints: str | None = None   # free-text, e.g. "no nuts this week"


class MealPlanResponse(BaseModel):
    id: str
    user_id: str
    days: int
    start_date: date
    end_date: date
    status: str
    meals: list[MealAssignment]
    constraint_summary: dict
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
