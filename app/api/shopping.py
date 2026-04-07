from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.shopping_list import ShoppingList, ShoppingListStatus
from app.schemas.shopping_list import MarkPurchasedRequest, ShoppingListResponse
from app.services import user_service

router = APIRouter(prefix="/users/{user_id}/plans/{plan_id}/shopping-list", tags=["shopping"])


@router.get("/", response_model=ShoppingListResponse)
async def get_shopping_list(
    user_id: str, plan_id: str, db: AsyncSession = Depends(get_db)
):
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.meal_plan_id == plan_id,
            ShoppingList.user_id == user_id,
        )
    )
    shopping_list = result.scalar_one_or_none()
    if not shopping_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shopping list not found for this plan.",
        )
    return shopping_list


@router.patch("/mark-purchased", response_model=ShoppingListResponse)
async def mark_purchased(
    user_id: str,
    plan_id: str,
    data: MarkPurchasedRequest,
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

    result = await db.execute(
        select(ShoppingList).where(
            ShoppingList.meal_plan_id == plan_id,
            ShoppingList.user_id == user_id,
        )
    )
    shopping_list = result.scalar_one_or_none()
    if not shopping_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Shopping list not found.")

    shopping_list.status = ShoppingListStatus.purchased
    shopping_list.purchased_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(shopping_list)
    return shopping_list
