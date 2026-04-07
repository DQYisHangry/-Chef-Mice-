from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import UserProfile
from app.schemas.user import UserCreate, UserPreferencesUpdate


async def create_user(db: AsyncSession, data: UserCreate) -> UserProfile:
    user = UserProfile(**data.model_dump())
    db.add(user)
    await db.flush()   # get the ID without committing (commit happens in get_db)
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: str) -> UserProfile | None:
    result = await db.execute(select(UserProfile).where(UserProfile.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> UserProfile | None:
    result = await db.execute(select(UserProfile).where(UserProfile.email == email))
    return result.scalar_one_or_none()


async def update_preferences(
    db: AsyncSession, user: UserProfile, data: UserPreferencesUpdate
) -> UserProfile:
    update_data = data.model_dump(exclude_none=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.flush()
    await db.refresh(user)
    return user
