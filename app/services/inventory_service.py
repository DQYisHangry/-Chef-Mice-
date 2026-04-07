from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.inventory import InventoryItem
from app.schemas.inventory import InventoryBulkUpsert, InventoryItemCreate, InventoryItemUpdate


async def get_inventory(db: AsyncSession, user_id: str) -> list[InventoryItem]:
    """Return active inventory items, soonest-expiring first."""
    result = await db.execute(
        select(InventoryItem)
        .where(InventoryItem.user_id == user_id, InventoryItem.is_active == True)  # noqa: E712
        .order_by(InventoryItem.expiration_date.asc().nullslast())
    )
    return list(result.scalars().all())


async def get_item(db: AsyncSession, item_id: str, user_id: str) -> InventoryItem | None:
    result = await db.execute(
        select(InventoryItem).where(
            InventoryItem.id == item_id,
            InventoryItem.user_id == user_id,
            InventoryItem.is_active == True,  # noqa: E712
        )
    )
    return result.scalar_one_or_none()


async def add_item(
    db: AsyncSession, user_id: str, data: InventoryItemCreate
) -> InventoryItem:
    item = InventoryItem(user_id=user_id, **data.model_dump())
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def update_item(
    db: AsyncSession, item: InventoryItem, data: InventoryItemUpdate
) -> InventoryItem:
    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    await db.flush()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item: InventoryItem) -> None:
    """Soft delete."""
    item.is_active = False
    await db.flush()


async def bulk_upsert(
    db: AsyncSession, user_id: str, data: InventoryBulkUpsert
) -> list[InventoryItem]:
    """
    Upsert by ingredient_name — update quantity if item already exists,
    otherwise create new. Used after a shopping trip.
    """
    existing = await get_inventory(db, user_id)
    existing_by_name = {i.ingredient_name.lower(): i for i in existing}

    results = []
    for item_data in data.items:
        key = item_data.ingredient_name.lower()
        if key in existing_by_name:
            existing_item = existing_by_name[key]
            existing_item.quantity = item_data.quantity
            existing_item.unit = item_data.unit
            existing_item.ingredient_type = item_data.ingredient_type
            existing_item.expiration_date = item_data.expiration_date
            await db.flush()
            await db.refresh(existing_item)
            results.append(existing_item)
        else:
            new_item = await add_item(db, user_id, item_data)
            results.append(new_item)

    return results


async def deduct_inventory(
    db: AsyncSession, user_id: str, deductions: list[dict]
) -> None:
    """
    Deduct ingredient quantities after a meal plan is confirmed.
    deductions: [{ingredient_name: str, quantity: float, unit: str}]
    Items that reach 0 are soft-deleted.
    """
    inventory = await get_inventory(db, user_id)
    inventory_by_name = {i.ingredient_name.lower(): i for i in inventory}

    for deduction in deductions:
        key = deduction["ingredient_name"].lower()
        if key not in inventory_by_name:
            continue
        item = inventory_by_name[key]
        item.quantity = max(0.0, item.quantity - deduction["quantity"])
        if item.quantity == 0.0:
            item.is_active = False

    await db.flush()
