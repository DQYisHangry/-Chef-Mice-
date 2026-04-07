from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.inventory import (
    InventoryBulkUpsert,
    InventoryItemCreate,
    InventoryItemResponse,
    InventoryItemUpdate,
)
from app.services import inventory_service, user_service

router = APIRouter(prefix="/users/{user_id}/inventory", tags=["inventory"])


async def _get_user_or_404(user_id: str, db: AsyncSession):
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.get("/", response_model=list[InventoryItemResponse])
async def list_inventory(user_id: str, db: AsyncSession = Depends(get_db)):
    await _get_user_or_404(user_id, db)
    return await inventory_service.get_inventory(db, user_id)


@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def add_inventory_item(
    user_id: str,
    data: InventoryItemCreate,
    db: AsyncSession = Depends(get_db),
):
    await _get_user_or_404(user_id, db)
    return await inventory_service.add_item(db, user_id, data)


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    user_id: str,
    item_id: str,
    data: InventoryItemUpdate,
    db: AsyncSession = Depends(get_db),
):
    await _get_user_or_404(user_id, db)
    item = await inventory_service.get_item(db, item_id, user_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
    return await inventory_service.update_item(db, item, data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    user_id: str,
    item_id: str,
    db: AsyncSession = Depends(get_db),
):
    await _get_user_or_404(user_id, db)
    item = await inventory_service.get_item(db, item_id, user_id)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
    await inventory_service.delete_item(db, item)


@router.post("/bulk", response_model=list[InventoryItemResponse])
async def bulk_upsert_inventory(
    user_id: str,
    data: InventoryBulkUpsert,
    db: AsyncSession = Depends(get_db),
):
    """
    Bulk upsert after a shopping trip.
    Existing items (matched by name) get their quantity updated.
    New items are created.
    """
    await _get_user_or_404(user_id, db)
    return await inventory_service.bulk_upsert(db, user_id, data)
