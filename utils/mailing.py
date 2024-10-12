from aiogram import Bot

from database.models import Task
from database.requests.user import get_users
from keyboard.inline.task import task_acceptance


async def mailing_task(bot: Bot, task: Task):
    users = await get_users()
    for user in users:
        await bot.send_message(user.tg_id,
                               text=f"<b>{task.title} | {task.reward}₽\n\n"
                                      f"📋{task.text}\n\n"
                                      f"⚒️{task.category.name}</b>",
                               reply_markup=await task_acceptance(task_id=task.id)
                               )
