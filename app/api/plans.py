from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.meal_plan import MealPlan, MealPlanStatus
from app.schemas.meal_plan import MealPlanResponse, PlanRequest
from app.services import user_service

router = APIRouter(prefix="/users/{user_id}/plans", tags=["plans"])


async def _get_user_or_404(user_id: str, db: AsyncSession):
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user


@router.get("/", response_model=list[MealPlanResponse])
async def list_plans(user_id: str, db: AsyncSession = Depends(get_db)):
    await _get_user_or_404(user_id, db)
    result = await db.execute(
        select(MealPlan)
        .where(MealPlan.user_id == user_id)
        .order_by(MealPlan.created_at.desc())
    )
    return list(result.scalars().all())


@router.get("/{plan_id}", response_model=MealPlanResponse)
async def get_plan(user_id: str, plan_id: str, db: AsyncSession = Depends(get_db)):
    await _get_user_or_404(user_id, db)
    result = await db.execute(
        select(MealPlan).where(MealPlan.id == plan_id, MealPlan.user_id == user_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found.")
    return plan


@router.post("/", response_model=MealPlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(
    user_id: str,
    request: PlanRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Trigger the planning agent.
    Agent implementation added in Milestone 3.
    """
    await _get_user_or_404(user_id, db)
    # TODO (Milestone 3): replace with orchestrator.run(user_id, request, db)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Planning agent not yet implemented. Coming in Milestone 3.",
    )


@router.post("/{plan_id}/confirm", response_model=MealPlanResponse)
async def confirm_plan(user_id: str, plan_id: str, db: AsyncSession = Depends(get_db)):
    """
    Confirm a draft plan → deduct ingredients from inventory.
    """
    await _get_user_or_404(user_id, db)
    result = await db.execute(
        select(MealPlan).where(MealPlan.id == plan_id, MealPlan.user_id == user_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found.")
    if plan.status != MealPlanStatus.draft:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Plan is already {plan.status}, cannot confirm.",
        )
    # TODO (Milestone 3): deduct_inventory(db, user_id, plan)
    plan.status = MealPlanStatus.confirmed
    await db.flush()
    await db.refresh(plan)
    return plan


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_plan(user_id: str, plan_id: str, db: AsyncSession = Depends(get_db)):
    await _get_user_or_404(user_id, db)
    result = await db.execute(
        select(MealPlan).where(MealPlan.id == plan_id, MealPlan.user_id == user_id)
    )
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Plan not found.")
    if plan.status == MealPlanStatus.confirmed:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot cancel a confirmed plan.",
        )
    await db.delete(plan)
