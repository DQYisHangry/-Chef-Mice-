from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, Field

from app.models.inventory import IngredientType


class InventoryItemCreate(BaseModel):
    ingredient_name: str = Field(..., min_length=1, max_length=255)
    quantity: Annotated[float, Field(gt=0)]
    unit: str = Field(..., min_length=1, max_length=50)
    ingredient_type: IngredientType = IngredientType.shelf_stable
    expiration_date: date | None = None


class InventoryItemUpdate(BaseModel):
    """Partial update."""
    quantity: Annotated[float, Field(gt=0)] | None = None
    unit: str | None = None
    ingredient_type: IngredientType | None = None
    expiration_date: date | None = None


class InventoryItemResponse(BaseModel):
    id: str
    user_id: str
    ingredient_name: str
    quantity: float
    unit: str
    ingredient_type: str
    expiration_date: date | None
    is_active: bool
    added_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InventoryBulkUpsert(BaseModel):
    """Used when a user returns from the grocery store and updates everything at once."""
    items: list[InventoryItemCreate] = Field(..., min_length=1)
