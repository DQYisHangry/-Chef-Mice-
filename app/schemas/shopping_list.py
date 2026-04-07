from datetime import datetime

from pydantic import BaseModel


class ShoppingListItem(BaseModel):
    ingredient: str
    quantity: float
    unit: str
    reason: str       # "needed for Pasta Primavera on Day 3"
    category: str     # "produce", "dairy", "meat", "pantry", "frozen"


class ShoppingListResponse(BaseModel):
    id: str
    meal_plan_id: str
    user_id: str
    items: list[ShoppingListItem]
    status: str
    purchased_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class MarkPurchasedRequest(BaseModel):
    """Optionally specify which item indices were purchased; empty = mark all."""
    item_indices: list[int] | None = None
