import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.sqlite import JSON

from app.database import Base


class ShoppingListStatus(str, Enum):
    pending = "pending"
    purchased = "purchased"


class ShoppingList(Base):
    """
    Generated shopping list for a meal plan.

    items: [
        {
            ingredient: str,
            quantity: float,
            unit: str,
            reason: str,        # "needed for Pasta Primavera on Day 3"
            category: str,      # "produce", "dairy", "pantry" — for grouping
        }
    ]
    """
    __tablename__ = "shopping_lists"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    meal_plan_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("meal_plans.id", ondelete="CASCADE"),
        unique=True,   # one shopping list per meal plan
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True
    )

    # List of items with reason + category attached
    items: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default=ShoppingListStatus.pending
    )
    purchased_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    meal_plan: Mapped["MealPlan"] = relationship(back_populates="shopping_list")  # noqa: F821

    def __repr__(self) -> str:
        return f"<ShoppingList id={self.id} items={len(self.items)} status={self.status}>"
