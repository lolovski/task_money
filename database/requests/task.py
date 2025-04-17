from typing import Optional

from sqlalchemy import select

from database.models import async_session, User, Task, ActiveTask, PendingTask


async def set_task(data):
    async with async_session() as session:
        task = Task(title=data['title'], text=data['text'], description_url=data['description_url'], category_id=int(data['category_id']), reward=int(data['reward']), limit=int(data['limit']))
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task


async def get_task(task_id: int) -> Optional[Task]:
    async with async_session() as session:
        task = await session.scalar(select(Task).where(Task.id == int(task_id)))
        return task


async def get_tasks() -> list[Task]:
    async with async_session() as session:
        tasks = await session.scalars(select(Task))
        return tasks.all()


async def delete_task(task_id: int):
    async with async_session() as session:
        pending_users = []
        active_users = []

        task = await session.scalar(select(Task).where(Task.id == int(task_id)))
        active_tasks = await session.scalars(select(ActiveTask).where(ActiveTask.task_id == int(task.id)))

        active_tasks = active_tasks.all()

        active_tasks_user_id = [x.user_id for x in active_tasks]
        if active_tasks is not None:
            active_users = await session.scalars(select(User).where(User.id.in_(active_tasks_user_id)))
            active_users = active_users.all()
            for user in active_users:
                user.executable_task_id = None

        pending_tasks = await session.scalars(select(PendingTask).where(PendingTask.task_id == int(task_id)))
        pending_tasks = pending_tasks.all()
        pending_tasks_user_id = [x.user_id for x in pending_tasks]
        if pending_tasks is not None:
            pending_users = await session.scalars(select(User).where(User.id.in_(pending_tasks_user_id)))
            pending_users = pending_users.all()
        if task is not None:
            await session.delete(task)
        await session.commit()
        for user in active_users:
            await session.refresh(user)
        for user in pending_users:
            await session.refresh(user)

        return active_users, pending_users, task


async def set_active_task(task_id: int, tg_id: str):
    async with async_session() as session:
        task: Task = await session.scalar(select(Task).where(Task.id == int(task_id)))
        user: User = await session.scalar(select(User).where(User.tg_id == str(tg_id)))
        if task.limit > task.count_active:
            user.executable_task_id = int(task.id)
            task.count_active += 1
            active_task = ActiveTask(
               user_id=int(user.id),
               task_id=int(task.id),
            )
            session.add(active_task)
            await session.commit()
            return active_task
        else:
            return None

async def set_pending_task(task_id: int):
    async with async_session() as session:
        task: Task = await session.scalar(select(Task).where(Task.id == int(task_id)))
        active_task = await session.scalar(select(ActiveTask).where(ActiveTask.task_id == int(task_id)))
        user: User = await session.scalar(select(User).where(User.id == int(active_task.user_id)))
        user.executable_task_id = None
        user.executed_tasks.append(task)
        pending_task = PendingTask(
            user_id=int(user.id),
            task_id=int(task.id),
        )
        await session.delete(active_task)
        session.add(pending_task)
        await session.commit()
        await session.refresh(pending_task)
        await session.refresh(task)
        return task, pending_task


async def get_active_tasks():
    async with async_session() as session:
        active_tasks = await session.scalars(select(ActiveTask))
        return active_tasks.all()


async def get_pending_tasks():
    async with async_session() as session:
        pending_tasks = await session.scalars(select(PendingTask))
        return pending_tasks.all()


async def get_active_task(task_id: int):
    async with async_session() as session:
        active_task = await session.scalar(select(ActiveTask).where(ActiveTask.task_id == int(task_id)))
        return active_task

async def get_active_task_by_id(id: int):
    async with async_session() as session:
        active_task = await session.scalar(select(ActiveTask).where(ActiveTask.id == int(id)))
        return active_task

async def get_pending_task_by_id(id: int):
    async with async_session() as session:
        pending_task = await session.scalar(select(PendingTask).where(PendingTask.id == int(id)))
        return pending_task

async def get_pending_task(task_id: int):
    async with async_session() as session:
        pending_task = await session.scalar(select(PendingTask).where(PendingTask.task_id == int(task_id)))
        return pending_task


async def get_user_active_task(tg_id: str):
    async with async_session() as session:
        user: User = await session.scalar(select(User).where(User.tg_id == str(tg_id)))
        if user.executable_task_id is not None:
            task = await session.scalar(select(Task).where(Task.id == int(user.executable_task_id)))
            return task
        return None


async def cancel_executed_task(task_id: int):
    async with async_session() as session:
        task: Task = await session.scalar(select(Task).where(Task.id == int(task_id)))

        active_task = await session.scalar(select(ActiveTask).where(ActiveTask.task_id == int(task_id)))
        user = await session.scalar(select(User).where(User.id == int(active_task.user_id)))
        user.executable_task_id = None
        task.count_active -= 1
        await session.delete(active_task)
        await session.commit()
        await session.refresh(user)
        return user



async def cancel_pending_task(task_id: int):
    async with async_session() as session:
        task: Task = await session.scalar(select(Task).where(Task.id == int(task_id)))

        pending_task = await session.scalar(select(PendingTask).where(PendingTask.task_id == int(task_id)))
        user: User = await session.scalar(select(User).where(User.id == int(pending_task.user_id)))
        user.executed_tasks.remove(task)
        task.count_active -= 1
        await session.delete(pending_task)
        await session.commit()
        await session.refresh(user)
        return user


async def complete_pending_task(task_id: int):
    async with async_session() as session:
        referral = None
        task: Task = await session.scalar(select(Task).where(Task.id == int(task_id)))

        pending_task = await session.scalar(select(PendingTask).where(PendingTask.task_id == int(task_id)))
        user = await session.scalar(select(User).where(User.id == int(pending_task.user_id)))
        user.balance += int(task.reward)
        await session.delete(pending_task)
        if user.referral_id is not None:
            referral = await session.scalar(select(User).where(User.id == int(user.referral_id)))
            if referral is not None:
                print(task.reward, referral.referral_percent)
                referral.balance += (int(task.reward) * (referral.referral_percent / 100))

        await session.commit()
        if referral is not None:
            await session.refresh(referral)
        await session.refresh(user)
        return user, referral

