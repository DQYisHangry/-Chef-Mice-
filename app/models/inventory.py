import uuid
from datetime import date, datetime
from enum import Enum

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class IngredientType(str, Enum):
    perishable = "perishable"       # dairy, meat, fresh produce
    shelf_stable = "shelf_stable"   # canned goods, pasta, rice
    spice = "spice"                 # herbs, spices — rarely expires meaningfully
    frozen = "frozen"


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("user_profiles.id", ondelete="CASCADE"), index=True
    )

    ingredient_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False)  # g, ml, count, tbsp, cup
    ingredient_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default=IngredientType.shelf_stable
    )
    expiration_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Soft delete — never hard-remove inventory rows
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    # Relationships
    user: Mapped["UserProfile"] = relationship(back_populates="inventory_items")  # noqa: F821

    def __repr__(self) -> str:
        return f"<InventoryItem {self.ingredient_name} qty={self.quantity}{self.unit}>"
