import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.sqlite import JSON

from app.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)

    # Stored as JSON arrays
    dietary_restrictions: Mapped[list] = mapped_column(JSON, default=list)
    cuisine_preferences: Mapped[list] = mapped_column(JSON, default=list)
    disliked_ingredients: Mapped[list] = mapped_column(JSON, default=list)

    # 1 = only familiar foods, 5 = try anything new
    adventurousness: Mapped[int] = mapped_column(Integer, default=3)

    # Household size / default servings per meal
    servings_per_meal: Mapped[int] = mapped_column(Integer, default=2)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    inventory_items: Mapped[list["InventoryItem"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )
    meal_plans: Mapped[list["MealPlan"]] = relationship(  # noqa: F821
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<UserProfile id={self.id} email={self.email}>"
