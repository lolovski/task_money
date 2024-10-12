from typing import List

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from task_money.database.models import Task


async def actuality_admin_tasks_keyboard(tasks: List[Task], current_page, count_page):
    keyboard = InlineKeyboardBuilder()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(text=f"{task.id} {task.title}", callback_data=f'actuality admin task {task.id}'))
    if (current_page == 0) and (count_page > 1):
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Вперед', callback_data=f'actuality admin next page task {current_page}'))

    elif (current_page + 1 == count_page) and (count_page > 1):
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'actuality admin last page task {current_page}'))

    elif count_page < 2:
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
    else:
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'actuality admin last page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Вперед', callback_data=f'actuality admin next page task {current_page}'))
    return keyboard.adjust(1, 1, 1, 1, 2, 3).as_markup()


async def active_admin_tasks_keyboard(tasks: List[Task], current_page, count_page):
    keyboard = InlineKeyboardBuilder()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(text=f"{task.id} {task.title}", callback_data=f'active admin task {task.id}'))
    if (current_page == 0) and (count_page > 1):
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'active admin cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Вперед', callback_data=f'admin next page task {current_page}'))

    elif (current_page + 1 == count_page) and (count_page > 1):
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'active admin last page task {current_page}'))

    elif count_page < 2:
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
    else:
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'active admin last page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Вперед', callback_data=f'active admin next page task {current_page}'))
    return keyboard.adjust(1, 1, 1, 1, 2, 3).as_markup()


async def pending_admin_tasks_keyboard(tasks: List[Task], current_page, count_page):
    keyboard = InlineKeyboardBuilder()
    for task in tasks:
        keyboard.add(InlineKeyboardButton(text=f"{task.id} {task.title}", callback_data=f'pending admin task {task.id}'))
    if (current_page == 0) and (count_page > 1):
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Вперед', callback_data=f'pending admin next page task {current_page}'))

    elif (current_page + 1 == count_page) and (count_page > 1):
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'pending admin last page task {current_page}'))

    elif count_page < 2:
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
    else:
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'pending admin last page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Отмена', callback_data=f'admin cancel page task {current_page}'))
        keyboard.add(InlineKeyboardButton(text='Вперед', callback_data=f'pending admin next page task {current_page}'))
    return keyboard.adjust(1, 1, 1, 1, 2, 3).as_markup()


async def actuality_task_keyboard(task):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=f'actuality admin delete task {task.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'return actuality admin task {task.id}'))
    return keyboard.as_markup()


async def active_tasks_keyboard(active_tasks, task_id):
    keyboard = InlineKeyboardBuilder()
    for task in active_tasks:
        keyboard.add(InlineKeyboardButton(text=f"Юзер {task.user_id}", callback_data=f'this active task {task.id}'))
    keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=f'active admin delete task {task_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'return active admin task'))
    return keyboard.adjust(2).as_markup()


async def pending_tasks_keyboard(pending_tasks, task_id):
    keyboard = InlineKeyboardBuilder()
    for task in pending_tasks:
        keyboard.add(InlineKeyboardButton(text=f"Юзер {task.user_id}", callback_data=f'this pending task {task.id}'))

    keyboard.add(InlineKeyboardButton(text='Удалить', callback_data=f'pending admin delete task {task_id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'return pending admin task'))
    return keyboard.adjust(2).as_markup()


async def active_task_keyboard(task):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Отменить выполнение', callback_data=f'active admin cancel task {task.id}'))
    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'return active admin task {task.id}'))
    return keyboard.adjust(1).as_markup()


async def pending_task_keyboard(task):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(text='Завершить', callback_data=f'pending admin complete task {task.id}'))
    keyboard.add(InlineKeyboardButton(text='Отменить выполнение', callback_data=f'pending admin cancel task {task.id}'))

    keyboard.add(InlineKeyboardButton(text='Назад', callback_data=f'return pending admin task {task.id}'))

    return keyboard.adjust(1).as_markup()
