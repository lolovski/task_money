from typing import Optional

from database.models import async_session, User, Task, PendingTask
from sqlalchemy import select


async def set_user(tg_id, username, referral_id: str = None):
    async with async_session() as session:
        if referral_id is not None:
            user = await session.scalar(select(User).where(User.tg_id == str(referral_id)))
            session.add(User(tg_id=str(tg_id), username=str(username), referral_id=user.id))
        else:
            session.add(User(tg_id=str(tg_id), username=str(username)))
        await session.commit()


async def get_id(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == str(tg_id)))
        return user.id


async def get_user_by_tg_id(tg_id) -> Optional[User]:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == str(tg_id)))
        if user is None:
            return None
        return user


async def get_profile(tg_id):
    async with async_session() as session:
        user: User = await session.scalar(select(User).where(User.tg_id == str(tg_id)))
        if user is None:
            return None
        pending_tasks = await session.scalars(select(PendingTask).where(PendingTask.user_id == user.id))
        pending_tasks = pending_tasks.all()
        tasks_id = [x.task_id for x in pending_tasks]
        tasks = await session.scalars(select(Task).where(Task.id.in_(tasks_id)))
        count_ref = await session.scalars(select(User).where(User.referral_id == int(user.id)))
        return user, tasks.all(), len(count_ref.all())


async def debit(tg_id, money):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == str(tg_id)))
        user.balance -= money
        await session.commit()


async def add_money(tg_id, money):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == str(tg_id)))
        user.balance += money
        await session.commit()


async def get_users():
    async with async_session() as session:
        users = await session.scalars(select(User))
        return users.all()


async def get_user(user_id):
    async with async_session() as session:

        user = await session.scalar(select(User).where(User.id == int(user_id)))
        return user


async def get_profile_by_id(user_id):
    async with async_session() as session:
        user: User = await session.scalar(select(User).where(User.id == int(user_id)))
        if user is None:
            return None
        pending_tasks = await session.scalars(select(PendingTask).where(PendingTask.user_id == user.id))
        pending_tasks = pending_tasks.all()
        tasks_id = [x.task_id for x in pending_tasks]
        tasks = await session.scalars(select(Task).where(Task.id.in_(tasks_id)))
        count_ref = await session.scalars(select(User).where(User.referral_id == int(user.id)))
        return user, tasks.all(), len(count_ref.all())


async def change_referral_percent(ref_percent, user_id):
    async with async_session() as session:
        user: User = await session.scalar(select(User).where(User.id == int(user_id)))
        user.referral_percent = ref_percent
        await session.commit()
