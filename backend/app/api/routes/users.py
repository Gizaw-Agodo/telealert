from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db_session)) -> User:
    # Check if user already exists
    result = await db.execute(select(User).where(User.telegram_id == user_in.telegram_id))
    existing_user: User | None = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this Telegram ID already exists."
        )

    # Create new user
    new_user = User(**user_in.model_dump())
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/{telegram_id}", response_model=UserResponse)
async def get_user_by_telegram_id(telegram_id: int, db: AsyncSession = Depends(get_db_session)) -> User:
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user: User | None = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    return user