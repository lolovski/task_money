from typing import Optional, List

from task_money.database.models import async_session, User, Task, Category, ActiveTask
from sqlalchemy import select


async def get_category(category_id: int) -> Optional[Category]:
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.id == int(category_id)))
        return category


async def get_categories() -> List[Category]:
    async with async_session() as session:
        categories = await session.scalars(select(Category))
        return categories.all()


async def set_category(name: str):
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.name == str(name)))
        if category is None:
            category = Category(name=name)
            session.add(category)
            await session.commit()
            await session.refresh(category)
            return category.id
        else:
            return category.id


async def get_category_tasks(tg_id: str, category_name: str = None, category=None):
    async with async_session() as session:
        if category is None:
            category = await session.scalar(select(Category).where(Category.name == str(category_name)))

        if category is not None:
            user: User = await session.scalar(select(User).where(User.tg_id == str(tg_id)))
            executed_tasks = user.executed_tasks

            executed_task_id = [x.id for x in executed_tasks]

            tasks = await session.scalars(
                select(Task)
                .where(Task.category_id == int(category.id),
                       Task.id.notin_(executed_task_id),
                       Task.count_active < Task.limit)
                .order_by(Task.reward.desc())
            )
            return tasks.all(), category
        else:
            return [], category


async def delete_category(category_id: int):
    async with async_session() as session:
        category = await session.scalar(select(Category).where(Category.id == int(category_id)))
        if category is not None:

            tasks = await session.scalars(select(Task).where(Task.category_id == int(category_id)))
            tasks = tasks.all()

            active_tasks = await session.scalars(select(ActiveTask).where(ActiveTask.task_id.in_(task.id for task in tasks)))
            active_tasks = active_tasks.all()

            active_tasks_user_id = [x.user_id for x in active_tasks]
            if active_tasks_user_id:
                active_users = await session.scalars(select(User).where(User.id.in_(active_tasks_user_id)))
                active_users = active_users.all()

                for user in active_users:
                    user.executable_task_id = None

            await session.commit()
            await session.delete(category)
            await session.commit()
        return category
