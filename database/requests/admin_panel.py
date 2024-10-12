from sqlalchemy import select

from database.models import async_session, User


async def add_balance(user_id, amount):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == int(user_id)))
        user.balance += int(amount)
        await session.commit()
        await session.refresh(user)
        return user.balance, user.tg_id


async def delete_balance(user_id, amount):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.id == int(user_id)))
        user.balance -= int(amount)
        await session.commit()
        await session.refresh(user)
        return user.balance, user.tg_id


