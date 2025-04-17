from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, ForeignKey, Integer, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, declared_attr
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncAttrs
import os
from sqlalchemy.sql import func
from dotenv import load_dotenv
load_dotenv()

engine = create_async_engine(os.getenv('DATABASE_URL'))
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class User(Base):
    tg_id: Mapped[str] = mapped_column(String(32))
    referral_id: Mapped[Optional[int]] = mapped_column(ForeignKey('user.id'), default=None, unique=False)
    referral_percent: Mapped[int] = mapped_column(Integer, default=10)
    username: Mapped[str] = mapped_column(String(64))
    reg_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    balance: Mapped[int] = mapped_column(Integer, default=0)
    executable_task_id: Mapped[Optional[int]] = mapped_column(ForeignKey('task.id'), default=None, unique=False)
    number_executed_tasks: Mapped[int] = mapped_column(Integer, default=0)
    executed_tasks: Mapped[List['Task']] = relationship(
        back_populates='users',
        secondary='usertask',
        lazy='selectin'
    )


class Task(Base):
    title: Mapped[str] = mapped_column(String(128))
    text: Mapped[str] = mapped_column(String(1024))
    description_url: Mapped[str] = mapped_column(String(256))
    reward: Mapped[int] = mapped_column(Integer)
    category_id: Mapped[int] = mapped_column(ForeignKey('category.id'))
    limit: Mapped[Optional[int]] = mapped_column(Integer, default=None)
    count_active: Mapped[int] = mapped_column(Integer, default=0)

    category: Mapped['Category'] = relationship(
        'Category',
        back_populates='tasks',
        lazy='selectin'
    )
    is_activ: Mapped[bool] = mapped_column(Boolean, default=False)
    is_pending: Mapped[bool] = mapped_column(Boolean, default=False)

    pending: Mapped[List['PendingTask']] = relationship(
        'PendingTask',
        back_populates='tasks',
        cascade='all'

    )
    active: Mapped[List['ActiveTask']] = relationship(
        'ActiveTask',
        back_populates='tasks',
        cascade='all'

    )
    users: Mapped[List['User']] = relationship(
        back_populates='executed_tasks',
        secondary='usertask',
        lazy='selectin'
    )


class UserTask(Base):
    user_id: Mapped[str] = mapped_column(ForeignKey('user.id', ondelete='CASCADE'))
    task_id: Mapped[str] = mapped_column(ForeignKey('task.id', ondelete='CASCADE'))



class Category(Base):
    name: Mapped[str] = mapped_column(String(32))
    tasks: Mapped[List[Task]] = relationship(
        'Task',
        back_populates='category',
        cascade='all'
    )


class PendingTask(Base):
    task_id:  Mapped[int] = mapped_column(ForeignKey('task.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    tasks: Mapped[Task] = relationship(
        'Task',
        back_populates='pending',
        lazy='selectin'
    )


class ActiveTask(Base):
    task_id: Mapped[int] = mapped_column(ForeignKey('task.id'))
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    start_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    tasks: Mapped[Task] = relationship(
        'Task',
        back_populates='active',
        lazy='selectin'
    )


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

