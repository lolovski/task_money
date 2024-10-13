from sqlalchemy import select

from database.models import async_session, User

from task_money.database.models import Task, ActiveTask, PendingTask


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


async def get_admin_stats():
    async with async_session() as session:
        users = await session.scalars(select(User))
        tasks = await session.scalars(select(Task))
        final_tasks = await session.scalars(select(Task).where(Task.limit == Task.count_active))
        active_tasks = await session.scalars(select(ActiveTask))
        pending_tasks = await session.scalars(select(PendingTask))
        total_balance = 0
        users = users.all()
        for user in users:
            total_balance += user.balance
        return len(users), len(tasks.all()), len(final_tasks.all()), len(active_tasks.all()), len(pending_tasks.all()), total_balance