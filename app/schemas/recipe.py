from datetime import datetime

from pydantic import BaseModel, Field

from app.models.recipe import RecipeSource


class RecipeIngredient(BaseModel):
    name: str
    quantity: float
    unit: str
    optional: bool = False


class RecipeResponse(BaseModel):
    id: str
    external_id: str | None
    source: str
    name: str
    description: str | None
    cuisine_types: list[str]
    dietary_tags: list[str]
    ingredients: list[RecipeIngredient]
    instructions: str
    prep_time_minutes: int
    cook_time_minutes: int
    servings: int
    cached_at: datetime

    model_config = {"from_attributes": True}


class RecipeSearchFilters(BaseModel):
    """Input to the RecipeProvider.search() interface."""
    cuisine_types: list[str] = Field(default_factory=list)
    dietary_tags: list[str] = Field(default_factory=list)
    max_prep_plus_cook_minutes: int | None = None
    include_ingredients: list[str] = Field(default_factory=list)
    exclude_ingredients: list[str] = Field(default_factory=list)
    max_results: int = 20
