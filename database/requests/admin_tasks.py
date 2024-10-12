from sqlalchemy import select

from database.models import async_session, Task, ActiveTask, PendingTask


async def get_actuality_tasks() -> list[Task]:
    async with async_session() as session:
        tasks = await session.scalars(
            select(Task)
            .order_by(Task.reward.desc())
        )
        return tasks.all()


async def get_active_tasks() -> list[Task]:
    async with async_session() as session:
        active_tasks = await session.scalars(select(ActiveTask))
        active_tasks = active_tasks.all()
        active_tasks_id = [x.task_id for x in active_tasks]
        tasks = await session.scalars(
            select(Task)
            .where(Task.id.in_(active_tasks_id))
            .order_by(Task.reward.desc())
        )
        return tasks.all()


async def get_pending_tasks() -> list[Task]:
    async with async_session() as session:
        pending_tasks = await session.scalars(select(PendingTask))
        pending_tasks = pending_tasks.all()
        pending_tasks_id = [x.task_id for x in pending_tasks]
        tasks = await session.scalars(
            select(Task)
            .where(Task.id.in_(pending_tasks_id))
            .order_by(Task.reward.desc())
        )
        return tasks.all()


async def get_this_active_tasks(task_id):
    async with async_session() as session:
        active_tasks = await session.scalars(
            select(ActiveTask)
            .where(ActiveTask.task_id == int(task_id))
            .order_by(ActiveTask.start_date.desc())
        )

        return active_tasks.all()


async def get_this_pending_tasks(task_id):
    async with async_session() as session:
        pending_tasks = await session.scalars(select(PendingTask).where(PendingTask.task_id == int(task_id)))

        return pending_tasks.all()