from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    dietary_restrictions: list[str] = Field(default_factory=list)
    cuisine_preferences: list[str] = Field(default_factory=list)
    disliked_ingredients: list[str] = Field(default_factory=list)
    adventurousness: Annotated[int, Field(ge=1, le=5)] = 3
    servings_per_meal: Annotated[int, Field(ge=1, le=20)] = 2


class UserPreferencesUpdate(BaseModel):
    """Partial update — all fields optional."""
    dietary_restrictions: list[str] | None = None
    cuisine_preferences: list[str] | None = None
    disliked_ingredients: list[str] | None = None
    adventurousness: Annotated[int, Field(ge=1, le=5)] | None = None
    servings_per_meal: Annotated[int, Field(ge=1, le=20)] | None = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    dietary_restrictions: list[str]
    cuisine_preferences: list[str]
    disliked_ingredients: list[str]
    adventurousness: int
    servings_per_meal: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
