import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.sqlite import JSON

from app.database import Base


class RecipeSource(str, Enum):
    local = "local"             # manually added
    spoonacular = "spoonacular"
    edamam = "edamam"
    llm = "llm"                 # LLM-generated fallback


class Recipe(Base):
    """
    Normalized recipe cache. All external API results are mapped into this schema
    before the agent ever sees them. The agent is fully decoupled from API specifics.
    """
    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    # Idempotency key — external API's own ID (e.g. Spoonacular recipe ID)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False, default=RecipeSource.local)

    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # JSON arrays of strings
    cuisine_types: Mapped[list] = mapped_column(JSON, default=list)   # ["italian", "mediterranean"]
    dietary_tags: Mapped[list] = mapped_column(JSON, default=list)    # ["vegan", "gluten-free"]

    # JSON: [{name: str, quantity: float, unit: str, optional: bool}]
    ingredients: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    instructions: Mapped[str] = mapped_column(Text, nullable=False, default="")
    prep_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    cook_time_minutes: Mapped[int] = mapped_column(Integer, default=0)
    servings: Mapped[int] = mapped_column(Integer, default=2)

    # Raw API response stored for debugging / re-normalization without re-fetching
    raw_api_response: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    cached_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Recipe id={self.id} name={self.name!r} source={self.source}>"
