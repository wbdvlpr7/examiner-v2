from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update as sql_update
from .models import User
from datetime import datetime


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, telegram_id: int) -> User | None:
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()

    async def create_user(self, telegram_id: int, username: str = None) -> User:
        user = User(telegram_id=telegram_id, username=username)
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def update_user_state(self, telegram_id: int, state: str, **kwargs):
        """Update user state and other fields"""
        # First check if user exists
        user = await self.get_user(telegram_id)

        if user is None:
            # Create new user if doesn't exist
            user = await self.create_user(telegram_id)

        # Update fields
        user.current_state = state
        user.last_interaction = datetime.utcnow()

        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)

        await self.session.commit()
        return user
